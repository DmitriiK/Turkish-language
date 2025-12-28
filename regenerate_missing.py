#!/usr/bin/env python3
"""
Regenerate missing examples for verbs with incomplete forms.
This script identifies missing files and regenerates them using specific tense filters.
Primary model: claude-haiku-4-5 (has quota)
Fallback model: claude-sonnet-4@20250514 (when Haiku exhausted)
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Set up logging to both console and file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = open(f'regeneration_output_{timestamp}.log', 'w', buffering=1)  # Line buffered

def log(message):
    """Print to both console and log file."""
    print(message)
    print(message, file=log_file)
    log_file.flush()  # Ensure immediate write

log("=" * 80)
log(f"TURKISH VERB REGENERATION - {datetime.now().isoformat()}")
log("=" * 80)
log("Primary Model: claude-sonnet-4-5@20250929")
log("Fallback Model: gemini-2.5-flash")
log("=" * 80)

# Load tense mapping
with open('data/tense_level_mapping.json') as f:
    tense_data = json.load(f)
all_tenses = list(tense_data.keys())

# Load verb index
with open('data/verbs_index.json') as f:
    verb_index = json.load(f)

pronouns = ['ben', 'sen', 'o', 'biz', 'siz', 'onlar']

# Get expected file counts from a reference complete verb (think)
reference_verb_dir = Path('data/output/training_examples_for_verbs/think')
expected_counts = {}
for tense in all_tenses:
    count = len(list(reference_verb_dir.glob(f'*_{tense}*.json')))
    expected_counts[tense] = count

def get_missing_tenses(verb_folder):
    """Get list of tenses that have missing examples for a verb."""
    verb_dir = Path(f'data/output/training_examples_for_verbs/{verb_folder}')
    
    if not verb_dir.exists():
        return all_tenses
    
    # Count how many files exist per tense
    tense_counts = {}
    for tense in all_tenses:
        count = len(list(verb_dir.glob(f'*_{tense}*.json')))
        tense_counts[tense] = count
    
    # Find tenses with missing files by comparing to expected counts
    missing_tenses = [tense for tense in all_tenses 
                     if tense_counts.get(tense, 0) < expected_counts.get(tense, 0)]
    
    return missing_tenses


# Process verbs 1-30
verbs_to_process = []

for verb_data in verb_index['verbs']:
    rank = verb_data['rank']
    if 1 <= rank <= 30:
        verb_folder = verb_data['folder_name']
        verb_dir = Path(f'data/output/training_examples_for_verbs/{verb_folder}')
        
        if not verb_dir.exists():
            file_count = 0
        else:
            file_count = len(list(verb_dir.glob('*.json')))
        
        if file_count < 182:
            missing_tenses = get_missing_tenses(verb_folder)
            if missing_tenses:
                verbs_to_process.append({
                    'rank': rank,
                    'folder': verb_folder,
                    'english': verb_data['verb_english'],
                    'missing_count': 182 - file_count,
                    'missing_tenses': missing_tenses
                })

log(f"\nFound {len(verbs_to_process)} verbs with missing examples in ranks 1-30\n")

for verb_info in sorted(verbs_to_process, key=lambda x: x['rank']):
    log(f"Rank {verb_info['rank']:2d}: {verb_info['english']:15s} ({verb_info['folder']})")
    log(f"           Missing: {verb_info['missing_count']} files")

log("\n" + "=" * 80)
log("Starting regeneration with Sonnet 4.5 (fallback to Gemini when quota exhausted)...")
log("=" * 80)

# Track which model was used for each verb
current_model = 'claude-sonnet-4-5@20250929'
stats = {
    'sonnet': {'verbs_completed': 0, 'files_created': 0},
    'gemini': {'verbs_completed': 0, 'files_created': 0},
    'skipped': 0,
    'failed': 0,
    'quota_switches': 0
}

for i, verb_info in enumerate(sorted(verbs_to_process, key=lambda x: x['rank']), 1):
    # Re-check missing files before processing (skip if already complete)
    verb_dir = Path(f'data/output/training_examples_for_verbs/{verb_info["folder"]}')
    current_count = len(list(verb_dir.glob('*.json'))) if verb_dir.exists() else 0
    
    if current_count >= 182:
        log(f"\n[{i}/{len(verbs_to_process)}] ✅ SKIP: {verb_info['english']} (rank {verb_info['rank']}) - Complete ({current_count}/182)")
        stats['skipped'] += 1
        continue
    
    log(f"\n[{i}/{len(verbs_to_process)}] Regenerating: {verb_info['english']} (rank {verb_info['rank']})")
    log(f"    Current: {current_count}/182 | Missing: {182 - current_count}")
    log(f"    Model: {current_model}")
    log(f"    Tenses: {', '.join(verb_info['missing_tenses'][:3])}{'...' if len(verb_info['missing_tenses']) > 3 else ''}")
    
    # Build command with explicit model
    env = os.environ.copy()
    env['DIAL_API_MODEL'] = current_model
    
    cmd = [
        'python', 'pipelines/create_traing_example.py',
        '--verbs', verb_info['english'],
        '--tenses', *verb_info['missing_tenses'],
        '--timeout-retries', '2'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes max per verb
            env=env
        )
        
        # Re-check actual file count after generation
        new_count = len(list(verb_dir.glob('*.json'))) if verb_dir.exists() else 0
        files_created = new_count - current_count
        
        if result.returncode == 0:
            if files_created > 0:
                model_key = 'sonnet' if 'sonnet' in current_model else 'gemini'
                log(f"    ✅ Success! Created {files_created} files ({new_count}/182)")
                stats[model_key]['verbs_completed'] += 1
                stats[model_key]['files_created'] += files_created
            else:
                log(f"    ⚠️  Completed but no files created (possible connection error)")
                if result.stderr:
                    if "ConnectionError" in result.stderr or "ConnectTimeout" in result.stderr:
                        log(f"       Error: Connection issue detected")
        else:
            # Check for quota error
            error_output = result.stderr.lower()
            if "429" in error_output or "quota" in error_output or "rate limit" in error_output:
                log(f"    ⏳ QUOTA LIMIT on {current_model}")
                # Switch models
                if 'sonnet' in current_model:
                    current_model = 'gemini-2.5-flash'
                    stats['quota_switches'] += 1
                    log(f"    🔄 Switching to: {current_model}")
                    # Retry this verb with new model
                    log(f"    ⟳  Retrying with Gemini...")
                    env['DIAL_API_MODEL'] = current_model
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, env=env)
                    new_count = len(list(verb_dir.glob('*.json'))) if verb_dir.exists() else 0
                    files_created = new_count - current_count
                    if result.returncode == 0 and files_created > 0:
                        log(f"    ✅ Success with Gemini! Created {files_created} files ({new_count}/182)")
                        stats['gemini']['verbs_completed'] += 1
                        stats['gemini']['files_created'] += files_created
                    else:
                        log(f"    ❌ Gemini also failed")
                        stats['failed'] += 1
                else:
                    log(f"    ❌ Both models exhausted, cannot continue")
                    break
            else:
                log(f"    ❌ Failed with return code {result.returncode}")
                if result.stderr:
                    error_lines = result.stderr.split('\n')
                    for line in error_lines[-3:]:
                        if line.strip():
                            log(f"       {line[:100]}")
                stats['failed'] += 1
    
    except subprocess.TimeoutExpired:
        log(f"    ⏱️  Timeout after 30 minutes")
        stats['failed'] += 1
    except Exception as e:
        log(f"    ⚠️  Error: {e}")
        stats['failed'] += 1

log("\n" + "=" * 80)
log("REGENERATION COMPLETE")
log("=" * 80)
log(f"\nStatistics:")
log(f"  Sonnet:             {stats['sonnet']['verbs_completed']} verbs, {stats['sonnet']['files_created']} files")
log(f"  Gemini:             {stats['gemini']['verbs_completed']} verbs, {stats['gemini']['files_created']} files")
log(f"  Quota switches:     {stats['quota_switches']}")
log(f"  Skipped (complete): {stats['skipped']}")
log(f"  Failed:             {stats['failed']}")
log(f"\n  Total files created: {stats['sonnet']['files_created'] + stats['gemini']['files_created']}")
log("=" * 80)
log_file.close()


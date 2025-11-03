#!/usr/bin/env python3
"""
Fix verb affix breakdowns in training examples.

This script corrects cases where vowel harmony connectors are missing from
the affix fields, causing the sum of parts to not equal verb_full length.

The fix: Add missing buffer vowels to the appropriate affix field.
"""

import json
from pathlib import Path
from typing import Dict
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def calculate_affix_lengths(data: Dict) -> tuple[int, int]:
    """Calculate total length of verb parts and compare to verb_full."""
    tv = data.get('turkish_verb', {})
    verb_full = tv.get('verb_full', '')
    
    root_len = len(tv.get('root', ''))
    neg_len = len(tv.get('negative_affix', '') or '')
    tense_len = len(tv.get('tense_affix', '') or '')
    personal_len = len(tv.get('personal_affix', '') or '')
    
    parts_sum = root_len + neg_len + tense_len + personal_len
    verb_full_len = len(verb_full)
    
    return parts_sum, verb_full_len


def fix_verb_affixes(data: Dict) -> tuple[Dict, bool]:
    """
    Fix verb affix breakdown by adding missing buffer vowels.
    
    Returns:
        tuple: (modified_data, was_modified)
    """
    tv = data.get('turkish_verb', {})
    verb_full = tv.get('verb_full', '')
    
    if not verb_full:
        return data, False
    
    parts_sum, verb_full_len = calculate_affix_lengths(data)
    
    if parts_sum == verb_full_len:
        # Already correct
        return data, False
    
    missing_chars = verb_full_len - parts_sum
    
    if missing_chars <= 0:
        # Parts are longer than verb_full - data corruption, skip
        logger.warning(f"Skipping {data.get('verb_english', 'unknown')}: parts longer than verb_full")
        return data, False
    
    if missing_chars > 2:
        # Too many missing characters - likely a different issue
        logger.warning(f"Skipping {data.get('verb_english', 'unknown')}: {missing_chars} missing chars (too many)")
        return data, False
    
    # Reconstruct the verb to find where buffer vowels should go
    root = tv.get('root', '')
    neg_affix = tv.get('negative_affix', '') or ''
    tense_affix = tv.get('tense_affix', '') or ''
    personal_affix = tv.get('personal_affix', '') or ''
    
    # Find the actual affixes in verb_full
    idx = 0
    
    # Root is at the start
    if not verb_full.startswith(root):
        logger.warning(f"Skipping {data.get('verb_english', 'unknown')}: verb doesn't start with root")
        return data, False
    idx += len(root)
    
    # Negative affix (if present)
    if neg_affix and verb_full[idx:idx+len(neg_affix)] == neg_affix:
        idx += len(neg_affix)
    elif neg_affix:
        logger.warning(f"Skipping {data.get('verb_english', 'unknown')}: negative affix not found at expected position")
        return data, False
    
    # Tense affix - may have buffer vowel before it
    if tense_affix:
        # Try to find tense_affix in verb_full starting from current position
        # It might have 0-2 buffer vowels before it
        found = False
        for buffer_len in range(3):  # Try 0, 1, or 2 buffer vowels
            test_idx = idx + buffer_len
            if verb_full[test_idx:test_idx+len(tense_affix)] == tense_affix:
                # Found it! Extract the actual tense affix with buffer
                actual_tense_affix = verb_full[idx:test_idx+len(tense_affix)]
                tv['tense_affix'] = actual_tense_affix
                idx = test_idx + len(tense_affix)
                found = True
                break
        
        if not found:
            logger.warning(f"Skipping {data.get('verb_english', 'unknown')}: tense affix not found")
            return data, False
    
    # Personal affix - remaining part of verb
    if personal_affix:
        remaining = verb_full[idx:]
        if remaining:
            tv['personal_affix'] = remaining
        else:
            logger.warning(f"Skipping {data.get('verb_english', 'unknown')}: no remaining chars for personal affix")
            return data, False
    
    # Verify the fix
    new_parts_sum, new_verb_full_len = calculate_affix_lengths(data)
    if new_parts_sum != new_verb_full_len:
        logger.warning(f"Fix failed for {data.get('verb_english', 'unknown')}: lengths still don't match")
        return data, False
    
    verb_info = f"{data.get('verb_english', 'unknown')} - {tv.get('personal_pronoun', '')}"
    tense_info = f"{tv.get('verb_tense', '')}: '{verb_full}'"
    logger.info(f"Fixed {verb_info} - {tense_info}")
    return data, True


def process_file(file_path: Path) -> tuple[bool, bool]:
    """
    Process a single JSON file.
    
    Returns:
        tuple: (was_processed, was_modified)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified_data, was_modified = fix_verb_affixes(data)
        
        if was_modified:
            # Write back the fixed data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=2)
            return True, True
        
        return True, False
    
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False, False


def main():
    """Main function to process all training example files."""
    base_dir = Path(__file__).parent.parent / 'data' / 'output' / 'training_examples_for_verbs'
    
    if not base_dir.exists():
        logger.error(f"Directory not found: {base_dir}")
        return
    
    logger.info(f"Scanning directory: {base_dir}")
    
    total_files = 0
    processed_files = 0
    modified_files = 0
    error_files = 0
    
    # Walk through all JSON files
    for json_file in base_dir.rglob('*.json'):
        total_files += 1
        was_processed, was_modified = process_file(json_file)
        
        if was_processed:
            processed_files += 1
            if was_modified:
                modified_files += 1
        else:
            error_files += 1
    
    logger.info("=" * 60)
    logger.info("Processing complete!")
    logger.info(f"Total files found: {total_files}")
    logger.info(f"Successfully processed: {processed_files}")
    logger.info(f"Modified (fixed): {modified_files}")
    logger.info(f"Errors: {error_files}")
    logger.info(f"Unchanged: {processed_files - modified_files}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()

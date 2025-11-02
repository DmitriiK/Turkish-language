#!/usr/bin/env python3
"""
Generate navigation index for Turkish verb learning app.
Creates a three-tier index structure:
1. Main verbs index (list of all verbs) - lightweight for initial page load
2. Per-verb indexes (all forms for each verb) - loaded on demand
3. Individual training example files - loaded when user selects specific form
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import re


def load_tense_level_mapping() -> Dict[str, str]:
    """Load the tense-to-level mapping from JSON file"""
    mapping_file = Path(__file__).parent.parent / "data" / "tense_level_mapping.json"
    
    if not mapping_file.exists():
        print(f"⚠️  Tense level mapping not found at {mapping_file}")
        return {}
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def scan_training_examples() -> tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Scan all training example files and create navigation structure.
    
    Returns:
        tuple: (verbs_list, per_verb_indexes)
            - verbs_list: List of verb metadata for main index
            - per_verb_indexes: Dict of per-verb detailed indexes
    """
    base_path = Path(__file__).parent.parent / "data" / "output" / "training_examples_for_verbs"
    verbs_list = []
    per_verb_indexes = {}
    
    # Load tense-to-level mapping
    tense_level_mapping = load_tense_level_mapping()
    
    print(f"Scanning directory: {base_path}")
    
    if not base_path.exists():
        print(f"Error: Directory {base_path} does not exist")
        return verbs_list, per_verb_indexes
    
    # Scan all verb directories
    for verb_dir in sorted(base_path.iterdir()):
        if not verb_dir.is_dir() or verb_dir.name.startswith('.'):
            continue
            
        print(f"Processing verb directory: {verb_dir.name}")
        
        # Parse files in this verb directory
        verb_basic_info, verb_detailed_index = scan_verb_directory(verb_dir, tense_level_mapping)
        
        if verb_basic_info and verb_detailed_index["examples"]:  # Only include verbs with actual files
            verbs_list.append(verb_basic_info)
            per_verb_indexes[verb_dir.name] = verb_detailed_index
    
    return verbs_list, per_verb_indexes


def scan_verb_directory(verb_dir: Path, tense_level_mapping: Dict[str, str]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Scan a single verb directory and extract all available combinations.
    
    Returns:
        tuple: (basic_info, detailed_index)
            - basic_info: Lightweight verb metadata for main verbs list
            - detailed_index: Detailed per-verb index with all examples
    """
    # Basic info for main verbs list
    basic_info = {
        "rank": 0,
        "verb_english": "",
        "verb_russian": "",
        "verb_infinitive": "",
        "folder_name": verb_dir.name
    }
    
    # Detailed index for per-verb file
    detailed_index = {
        "verb_english": "",
        "verb_russian": "",
        "verb_infinitive": "",
        "verb_rank": 0,
        "folder_name": verb_dir.name,
        "examples": []
    }
    
    # Pattern to match file names: {pronoun}_{infinitive}_{tense}[_olumsuz].json
    file_pattern = re.compile(r'^(.+?)_(.+?)_([a-zçğıöşü_]+)(_olumsuz)?\.json$')
    
    for file_path in verb_dir.glob("*.json"):
        if file_path.name.startswith('.'):
            continue
            
        match = file_pattern.match(file_path.name)
        if not match:
            print(f"  Warning: Could not parse file name: {file_path.name}")
            continue
            
        pronoun, infinitive, tense_raw, polarity_suffix = match.groups()
        
        # Strip _olumsuz from tense name if it's part of the tense itself
        if tense_raw.endswith('_olumsuz'):
            tense = tense_raw[:-8]  # Remove '_olumsuz' suffix (8 characters)
            polarity = 'negative'
        else:
            tense = tense_raw
            polarity = 'negative' if polarity_suffix == '_olumsuz' else 'positive'
        
        # Load the file to get metadata
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
                
            # Extract verb information from the first file
            if not basic_info["verb_english"]:
                basic_info["rank"] = data.get("verb_rank", 0)
                basic_info["verb_english"] = data.get("verb_english", "")
                basic_info["verb_russian"] = data.get("verb_russian", "")
                basic_info["verb_infinitive"] = data.get("verb_infinitive", infinitive)
                
                detailed_index["verb_english"] = basic_info["verb_english"]
                detailed_index["verb_russian"] = basic_info["verb_russian"]
                detailed_index["verb_infinitive"] = basic_info["verb_infinitive"]
                detailed_index["verb_rank"] = basic_info["rank"]
            
            # Get the actual tense from the JSON file (more reliable than filename parsing)
            # Fallback to filename parsing if JSON data is missing
            actual_tense = data.get("turkish_verb", {}).get("verb_tense") or tense
            actual_pronoun = data.get("turkish_verb", {}).get("personal_pronoun") or pronoun
            actual_polarity = data.get("turkish_verb", {}).get("polarity") or polarity
            
            # Add example to detailed index (minimal metadata for navigation only)
            detailed_index["examples"].append({
                "tense": actual_tense,
                "pronoun": actual_pronoun,
                "polarity": actual_polarity,
                "file_path": f"data/output/training_examples_for_verbs/{verb_dir.name}/{file_path.name}"
            })
            
            print(f"  Found: {pronoun} + {infinitive} + {tense} ({polarity})")
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"  Error reading {file_path.name}: {e}")
            continue
    
    # Sort examples by tense, polarity, pronoun for consistent ordering
    detailed_index["examples"] = sorted(
        detailed_index["examples"], 
        key=lambda x: (x["tense"], x["polarity"], x["pronoun"])
    )
    
    return basic_info, detailed_index


def save_navigation_indexes(verbs_list: List[Dict[str, Any]], per_verb_indexes: Dict[str, Dict[str, Any]]):
    """
    Save navigation indexes to JSON files for frontend use.
    Creates three-tier structure:
    1. Main verbs index - lightweight list of all verbs
    2. Per-verb indexes - detailed index for each verb
    3. Individual training examples (already exist)
    """
    # Save to frontend public directory
    frontend_public = Path(__file__).parent.parent / "frontend" / "public" / "data"
    frontend_public.mkdir(parents=True, exist_ok=True)

    # Create verb_indexes directory in data/output/ alongside training examples
    output_dir = Path(__file__).parent.parent / "data" / "output"
    verb_indexes_dir = output_dir / "verb_indexes"
    verb_indexes_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save main verbs index (lightweight)
    verbs_index_path = frontend_public / "verbs_index.json"
    verbs_index = {
        "total_verbs": len(verbs_list),
        "verbs": sorted(verbs_list, key=lambda x: x["rank"])
    }

    with open(verbs_index_path, 'w', encoding='utf-8') as f:
        json.dump(verbs_index, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Main verbs index saved to: {verbs_index_path}")
    print(f"   Size: {verbs_index_path.stat().st_size / 1024:.1f} KB")

    # 2. Save per-verb indexes
    print(f"\n📁 Saving per-verb indexes to: {verb_indexes_dir}")
    for folder_name, verb_index in per_verb_indexes.items():
        verb_index_path = verb_indexes_dir / f"{folder_name}.json"

        with open(verb_index_path, 'w', encoding='utf-8') as f:
            json.dump(verb_index, f, indent=2, ensure_ascii=False)

        print(f"   - {verb_index['verb_english']}: {len(verb_index['examples'])} examples "
              f"({verb_index_path.stat().st_size / 1024:.1f} KB)")

    # 3. Save summary for debugging/stats
    summary_path = frontend_public / "navigation_summary.json"
    summary = {
        "total_verbs": len(verbs_list),
        "total_indexes": len(per_verb_indexes),
        "verbs": []
    }

    for verb_info in sorted(verbs_list, key=lambda x: x["rank"]):
        folder_name = verb_info["folder_name"]
        if folder_name in per_verb_indexes:
            verb_index = per_verb_indexes[folder_name]
            # Get unique tenses
            tenses = sorted(list(set(ex["tense"] for ex in verb_index["examples"])))
            summary["verbs"].append({
                "rank": verb_info["rank"],
                "english": verb_info["verb_english"],
                "russian": verb_info["verb_russian"],
                "turkish": verb_info["verb_infinitive"],
                "folder": folder_name,
                "tenses": tenses,
                "total_examples": len(verb_index["examples"])
            })

    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Summary saved to: {summary_path}")

    return verbs_index_path


def main():
    """
    Main function to generate navigation indexes.
    Creates three-tier index structure for optimal frontend performance.
    """
    print("=== Turkish Verb Navigation Index Generator ===")
    print("📝 Creating three-tier index structure:")
    print("   1. Main verbs index (lightweight list)")
    print("   2. Per-verb indexes (detailed forms)")
    print("   3. Individual examples (already exist)")

    # Scan all training examples
    verbs_list, per_verb_indexes = scan_training_examples()

    print(f"\n📊 Found {len(verbs_list)} verbs with training data:")
    for verb_info in sorted(verbs_list, key=lambda x: x["rank"])[:10]:  # Show first 10
        folder_name = verb_info["folder_name"]
        if folder_name in per_verb_indexes:
            example_count = len(per_verb_indexes[folder_name]["examples"])
            print(f"  - {verb_info['verb_english']}: {example_count} examples")

    if len(verbs_list) > 10:
        print(f"  ... and {len(verbs_list) - 10} more verbs")

    # Save navigation indexes
    if verbs_list:
        output_path = save_navigation_indexes(verbs_list, per_verb_indexes)
        print("\n✅ Navigation indexes generated successfully!")
        print(f"📁 Main index: {output_path}")
        print("📁 Per-verb indexes: frontend/public/data/indexes/")
    else:
        print("\n❌ No verbs found with training data")


if __name__ == "__main__":
    main()

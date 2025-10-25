#!/usr/bin/env python3
"""
Fix verb_rank values in all training example JSON files.
Reads correct ranks from verbs.csv and updates JSON files.
"""

import json
import csv
from pathlib import Path
from typing import Dict

def load_verb_ranks(csv_path: str) -> Dict[str, int]:
    """Load verb ranks from CSV file"""
    verb_ranks = {}
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            rank = int(row['Rank'].strip())
            english = row[' English'].strip()
            verb_ranks[english] = rank
    return verb_ranks


def fix_json_files(output_dir: Path, verb_ranks: Dict[str, int]):
    """Fix verb_rank in all JSON files"""
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Iterate through all JSON files
    for json_file in output_dir.rglob("*.json"):
        try:
            # Read JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get verb_english
            verb_english = data.get('verb_english')
            if not verb_english:
                print(f"⚠️  No verb_english in {json_file}")
                error_count += 1
                continue
            
            # Get correct rank
            correct_rank = verb_ranks.get(verb_english)
            
            # Handle special cases for verbs without parentheses
            # These are likely old/duplicate files that should use the same rank
            # as their parenthetical versions
            if correct_rank is None:
                if verb_english == "to get":
                    correct_rank = verb_ranks.get("to get (receive)")
                    if correct_rank:
                        print(f"  Using rank from 'to get (receive)' for '{verb_english}'")
                elif verb_english == "to call":
                    correct_rank = verb_ranks.get("to call (phone)")
                    if correct_rank:
                        print(f"  Using rank from 'to call (phone)' for '{verb_english}'")
            
            if correct_rank is None:
                print(f"⚠️  Verb '{verb_english}' not found in CSV (file: {json_file.name})")
                error_count += 1
                continue
            
            # Check current rank
            current_rank = data.get('verb_rank')
            
            if current_rank == correct_rank:
                skipped_count += 1
                continue
            
            # Update rank
            data['verb_rank'] = correct_rank
            
            # Write back to file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Fixed {json_file.name}: {current_rank} → {correct_rank} ({verb_english})")
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {json_file}: {e}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Skipped (already correct): {skipped_count} files")
    print(f"  Errors: {error_count} files")
    print(f"{'='*60}")


def main():
    # Paths
    csv_path = "data/input/verbs.csv"
    output_dir = Path("data/output/training_examples_for_verbs")
    
    print("Loading verb ranks from CSV...")
    verb_ranks = load_verb_ranks(csv_path)
    print(f"Loaded {len(verb_ranks)} verbs")
    
    print("\nFixing JSON files...")
    fix_json_files(output_dir, verb_ranks)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

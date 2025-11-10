#!/usr/bin/env python3
"""
Fix tense_affix fields that incorrectly include personal_affix.

This script identifies and fixes cases where the LLM incorrectly included
the personal affix at the end of the tense_affix field.

Example:
  verb_full: "söyleyeceğiz"
  WRONG: tense_affix="yeceğiz", personal_affix="iz"
  RIGHT: tense_affix="yeceğ", personal_affix="iz"
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

def fix_tense_affix_overlap(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Check and fix tense_affix if it ends with personal_affix.
    
    Returns:
        (changed, reason) - whether data was modified and why
    """
    verb_data = data['turkish_verb']
    tense_affix = verb_data.get('tense_affix', '')
    personal_affix = verb_data.get('personal_affix')
    
    if not personal_affix or not tense_affix:
        return False, "No personal affix to check"
    
    # Check if tense_affix incorrectly ends with personal_affix
    if tense_affix.endswith(personal_affix):
        # Remove the personal_affix from end of tense_affix
        correct_tense_affix = tense_affix[:-len(personal_affix)]
        
        # Only fix if the remaining part makes sense (not empty or too short)
        if len(correct_tense_affix) >= 1:
            old_value = tense_affix
            verb_data['tense_affix'] = correct_tense_affix
            return True, f"Fixed: '{old_value}' -> '{correct_tense_affix}' (removed '{personal_affix}')"
    
    return False, "No overlap detected"

def process_directory(data_dir: Path) -> Dict[str, int]:
    """Process all JSON files in the data directory."""
    stats = {
        'total_files': 0,
        'files_fixed': 0,
        'files_unchanged': 0,
        'errors': 0
    }
    
    fixed_files = []
    
    # Process all verb directories
    for verb_dir in sorted(data_dir.iterdir()):
        if not verb_dir.is_dir():
            continue
        
        # Process all JSON files in verb directory
        for json_file in sorted(verb_dir.glob('*.json')):
            stats['total_files'] += 1
            
            try:
                # Read JSON file
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check and fix
                changed, reason = fix_tense_affix_overlap(data)
                
                if changed:
                    # Write back to file
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    stats['files_fixed'] += 1
                    verb_info = f"{data['verb_english']} ({data['turkish_verb']['verb_full']})"
                    fixed_files.append({
                        'file': json_file.name,
                        'verb': verb_info,
                        'reason': reason
                    })
                    print(f"✓ {json_file.name}: {reason}")
                else:
                    stats['files_unchanged'] += 1
            
            except Exception as e:
                stats['errors'] += 1
                print(f"✗ Error processing {json_file}: {e}")
    
    return stats, fixed_files

def main():
    """Main execution function."""
    print("=" * 80)
    print("Fixing tense_affix overlaps with personal_affix")
    print("=" * 80)
    print()
    
    data_dir = Path('data/output/training_examples_for_verbs')
    
    if not data_dir.exists():
        print(f"❌ Error: Directory not found: {data_dir}")
        return
    
    # Process all files
    stats, fixed_files = process_directory(data_dir)
    
    # Print summary
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total files checked: {stats['total_files']}")
    print(f"Files fixed: {stats['files_fixed']}")
    print(f"Files unchanged: {stats['files_unchanged']}")
    print(f"Errors: {stats['errors']}")
    print()
    
    if fixed_files:
        print(f"\n✅ Complete! Fixed {len(fixed_files)} files.")
        print("\nFixed files by verb:")
        current_verb = None
        for item in fixed_files:
            verb = item['verb'].split(' (')[0]
            if verb != current_verb:
                print(f"\n  {verb}:")
                current_verb = verb
            print(f"    - {item['file']}")
    else:
        print("✅ No files needed fixing - all tense affixes are correct!")

if __name__ == '__main__':
    main()

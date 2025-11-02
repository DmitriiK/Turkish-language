#!/usr/bin/env python3
"""
Fix verb_english field inconsistencies in JSON files.
Ensures all files use the correct verb names from verbs.csv.
"""

import json
import csv
from pathlib import Path
from collections import defaultdict


def load_verb_mapping():
    """Load the correct verb names and their directory mappings from CSV."""
    csv_path = Path('data/input/verbs.csv')
    verb_to_dir = {}  # Maps "to be" -> "be"
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            english = row[' English'].strip()  # Note: CSV has space before column name
            # Derive directory name from English verb
            # "to be" -> "be", "to get (receive)" -> "get_(receive)"
            if english.startswith('to '):
                dir_name = english[3:]  # Remove "to "
            else:
                dir_name = english
            
            # Handle special characters for directory names
            dir_name = dir_name.replace(' ', '_').replace(',', '').lower()
            
            verb_to_dir[dir_name] = english
    
    return verb_to_dir


def fix_verb_names():
    """Fix verb_english in all JSON files to match CSV."""
    data_dir = Path('data/output/training_examples_for_verbs')
    verb_mapping = load_verb_mapping()
    
    fixed_count = 0
    error_count = 0
    total_checked = 0
    
    print("🔧 Fixing verb_english inconsistencies...")
    print(f"{'='*70}\n")
    
    for verb_dir in sorted(data_dir.iterdir()):
        if not verb_dir.is_dir():
            continue
        
        dir_name = verb_dir.name
        correct_verb_english = verb_mapping.get(dir_name)
        
        if not correct_verb_english:
            print(f"⚠️  Warning: No mapping found for directory '{dir_name}'")
            continue
        
        for json_file in verb_dir.glob('*.json'):
            total_checked += 1
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                current_verb = data.get('verb_english', '')
                
                if current_verb != correct_verb_english:
                    # Fix the verb_english field
                    data['verb_english'] = correct_verb_english
                    
                    # Write back
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    fixed_count += 1
                    if fixed_count <= 10:  # Show first 10 fixes
                        print(f"✅ Fixed: {json_file.name}")
                        print(f"   '{current_verb}' → '{correct_verb_english}'")
            
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing {json_file}: {e}")
    
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f"Total files checked: {total_checked}")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*70}")


if __name__ == '__main__':
    fix_verb_names()

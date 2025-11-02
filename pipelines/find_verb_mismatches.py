#!/usr/bin/env python3
"""
Find all training examples where verb_full is not in the Turkish sentence.
These examples need to be regenerated.
"""

import json
from pathlib import Path
from collections import defaultdict

def find_mismatches():
    """Find all examples with verb_full not in sentence."""
    data_dir = Path('frontend/public/data/output/training_examples_for_verbs')
    
    mismatches_by_verb = defaultdict(list)
    total_checked = 0
    total_mismatches = 0
    
    for verb_dir in sorted(data_dir.iterdir()):
        if not verb_dir.is_dir():
            continue
        
        for json_file in sorted(verb_dir.glob('*.json')):
            total_checked += 1
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                verb_full = data['turkish_verb']['verb_full']
                sentence = data['turkish_example_sentence']
                
                # Check if verb_full is in the sentence (case-insensitive)
                if verb_full.lower() not in sentence.lower():
                    total_mismatches += 1
                    mismatches_by_verb[data['verb_english']].append({
                        'file': json_file.name,
                        'verb_full': verb_full,
                        'sentence': sentence,
                        'tense': data['turkish_verb']['verb_tense'],
                        'pronoun': data['turkish_verb']['personal_pronoun'],
                        'polarity': data['turkish_verb']['polarity']
                    })
            
            except Exception as e:
                print(f"❌ Error reading {json_file}: {e}")
    
    return mismatches_by_verb, total_checked, total_mismatches


def main():
    print("🔍 Finding verb mismatches in training examples...\n")
    
    mismatches_by_verb, total_checked, total_mismatches = find_mismatches()
    
    # Print summary
    print(f"{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f"Total files checked: {total_checked}")
    print(f"Files with mismatches: {total_mismatches}")
    print(f"Percentage: {total_mismatches / total_checked * 100:.2f}%")
    print(f"Verbs affected: {len(mismatches_by_verb)}")
    print()
    
    # Print details by verb
    print(f"{'='*70}")
    print(f"📋 MISMATCHES BY VERB")
    print(f"{'='*70}")
    
    for verb_english in sorted(mismatches_by_verb.keys()):
        mismatches = mismatches_by_verb[verb_english]
        print(f"\n{verb_english.upper()} ({len(mismatches)} mismatches)")
        print(f"{'-'*70}")
        
        for i, mismatch in enumerate(mismatches[:5], 1):  # Show first 5
            print(f"  {i}. File: {mismatch['file']}")
            print(f"     Verb full: '{mismatch['verb_full']}'")
            print(f"     Sentence: {mismatch['sentence'][:60]}...")
            print(f"     Tense: {mismatch['tense']}, Pronoun: {mismatch['pronoun']}, Polarity: {mismatch['polarity']}")
        
        if len(mismatches) > 5:
            print(f"  ... and {len(mismatches) - 5} more")
    
    # Save list to file for regeneration
    output_file = Path('mismatched_examples.json')
    output_data = []
    
    for verb_english, mismatches in mismatches_by_verb.items():
        for mismatch in mismatches:
            output_data.append({
                'verb_english': verb_english,
                'tense': mismatch['tense'],
                'pronoun': mismatch['pronoun'],
                'polarity': mismatch['polarity'],
                'file': mismatch['file']
            })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ Mismatch list saved to: {output_file}")
    print(f"   Total examples to regenerate: {len(output_data)}")


if __name__ == '__main__':
    main()

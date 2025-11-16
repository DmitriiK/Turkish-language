#!/usr/bin/env python3
"""
Validate training examples for consistency and correctness.

This script checks generated training examples for common errors:
- Verb root mismatch between metadata and Turkish sentence
- Missing blanks in fill-in-the-blank sentences
- Inconsistent negative affixes
- Missing or incorrect tense affixes

Usage:
    python pipelines/validate_training_examples.py --start-from 1 --top-n-verbs 10
    python pipelines/validate_training_examples.py --verbs "be,do,have"
    python pipelines/validate_training_examples.py --all
"""

import argparse
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_verbs_from_csv() -> List[Dict[str, Any]]:
    """Load verbs from CSV file."""
    verbs_file = Path(__file__).parent.parent / "data" / "input" / "verbs.csv"
    verbs = []
    
    with open(verbs_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            rank = int(row['Rank'].strip())
            english = row[' English'].strip()
            russian = row[' Russian'].strip()
            turkish = row[' Turkish'].strip()
            verbs.append({
                'rank': rank,
                'english': english,
                'russian': russian,
                'turkish': turkish
            })
    
    return verbs


def find_verb_directory(verb_english: str, base_dir: Path) -> Path:
    """Find the directory for a given verb."""
    possible_patterns = [
        verb_english.replace(', ', ',_'),
        verb_english.replace(' ', '_'),
        verb_english,
    ]
    
    for pattern in possible_patterns:
        for candidate in base_dir.iterdir():
            if not candidate.is_dir():
                continue
            if candidate.name == pattern:
                return candidate
    
    return None


def validate_verb_root_in_sentence(example: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if the verb root appears in the Turkish sentence.
    
    Returns:
        (is_valid, error_message)
    """
    verb_root = example['turkish_verb']['root']
    turkish_sentence = example['turkish_example_sentence']
    verb_full = example['turkish_verb']['verb_full']
    
    # Check if the full verb appears in the sentence
    if verb_full.lower() in turkish_sentence.lower():
        return True, ""
    
    # Check if root appears anywhere in the sentence
    if verb_root.lower() not in turkish_sentence.lower():
        return False, f"Verb root '{verb_root}' not found in sentence: '{turkish_sentence}'"
    
    return True, ""


def validate_blank_in_sentence(example: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if the blank sentence has proper blank placeholder.
    
    Returns:
        (is_valid, error_message)
    """
    blank_sentence = example.get('turkish_example_sentence_with_blank', '')
    
    if not blank_sentence:
        return False, "Missing 'turkish_example_sentence_with_blank' field"
    
    # Check if blank contains underscore placeholder
    if '______' not in blank_sentence and '___' not in blank_sentence:
        return False, f"No blank placeholder in: '{blank_sentence}'"
    
    # Check if blank sentence is identical to full sentence
    full_sentence = example['turkish_example_sentence']
    if blank_sentence == full_sentence:
        return False, f"Blank sentence identical to full sentence: '{blank_sentence}'"
    
    return True, ""


def validate_verb_construction(example: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that verb_full can be constructed from its parts.
    
    Returns:
        (is_valid, error_message)
    """
    verb_data = example['turkish_verb']
    verb_full = verb_data['verb_full']
    root = verb_data['root']
    negative_affix = verb_data.get('negative_affix')
    tense_affix = verb_data.get('tense_affix')
    personal_affix = verb_data.get('personal_affix')
    
    # Build expected verb from parts
    parts = [root]
    if negative_affix:
        parts.append(negative_affix)
    if tense_affix:
        parts.append(tense_affix)
    if personal_affix:
        parts.append(personal_affix)
    
    # Check if all parts appear in verb_full in order
    constructed = ''.join(parts)
    
    # Allow for vowel harmony variations, but check basic structure
    if verb_full.lower() != constructed.lower():
        # Check if parts at least appear in the verb_full
        current_pos = 0
        for part in parts:
            if part and part.lower() not in verb_full.lower()[current_pos:]:
                return False, f"Part '{part}' not found in verb_full '{verb_full}' (expected: {constructed})"
            if part:
                idx = verb_full.lower().find(part.lower(), current_pos)
                if idx >= 0:
                    current_pos = idx + len(part)
    
    return True, ""


def validate_negative_polarity(example: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if negative polarity has negative_affix.
    
    Returns:
        (is_valid, error_message)
    """
    polarity = example['turkish_verb'].get('polarity')
    negative_affix = example['turkish_verb'].get('negative_affix')
    
    if polarity == 'negative' and not negative_affix:
        return False, "Negative polarity but no negative_affix specified"
    
    if polarity == 'positive' and negative_affix:
        return False, f"Positive polarity but has negative_affix: '{negative_affix}'"
    
    return True, ""


def validate_example(example: Dict[str, Any], file_path: Path) -> List[Dict[str, Any]]:
    """
    Validate a single training example.
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Validation 1: Verb root in sentence
    is_valid, error_msg = validate_verb_root_in_sentence(example)
    if not is_valid:
        errors.append({
            'file': file_path.name,
            'type': 'VERB_ROOT_MISMATCH',
            'severity': 'ERROR',
            'message': error_msg,
            'verb_full': example['turkish_verb']['verb_full'],
            'root': example['turkish_verb']['root']
        })
    
    # Validation 2: Blank placeholder
    is_valid, error_msg = validate_blank_in_sentence(example)
    if not is_valid:
        errors.append({
            'file': file_path.name,
            'type': 'BLANK_MISSING',
            'severity': 'ERROR',
            'message': error_msg
        })
    
    # Validation 3: Verb construction
    is_valid, error_msg = validate_verb_construction(example)
    if not is_valid:
        errors.append({
            'file': file_path.name,
            'type': 'VERB_CONSTRUCTION',
            'severity': 'WARNING',
            'message': error_msg
        })
    
    # Validation 4: Negative polarity
    is_valid, error_msg = validate_negative_polarity(example)
    if not is_valid:
        errors.append({
            'file': file_path.name,
            'type': 'POLARITY_MISMATCH',
            'severity': 'ERROR',
            'message': error_msg
        })
    
    return errors


def validate_verb(verb_english: str, base_dir: Path) -> List[Dict[str, Any]]:
    """
    Validate all examples for a single verb.
    
    Returns:
        List of validation errors
    """
    verb_dir = find_verb_directory(verb_english, base_dir)
    
    if not verb_dir:
        logger.warning(f"No directory found for verb: {verb_english}")
        return []
    
    all_errors = []
    json_files = list(verb_dir.glob("*.json"))
    
    logger.info(f"Validating {len(json_files)} examples for verb '{verb_english}'")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                example = json.load(f)
            
            errors = validate_example(example, json_file)
            if errors:
                all_errors.extend(errors)
        except Exception as e:
            logger.error(f"Failed to validate {json_file}: {e}")
            all_errors.append({
                'file': json_file.name,
                'type': 'PARSE_ERROR',
                'severity': 'ERROR',
                'message': str(e)
            })
    
    return all_errors


def generate_validation_report(all_errors: List[Dict[str, Any]], output_file: Path):
    """Generate and save validation report."""
    # Group errors by type
    errors_by_type = defaultdict(list)
    for error in all_errors:
        errors_by_type[error['type']].append(error)
    
    # Generate report
    report = {
        'summary': {
            'total_errors': len(all_errors),
            'errors_by_type': {
                error_type: len(errors) 
                for error_type, errors in errors_by_type.items()
            },
            'errors_by_severity': {
                'ERROR': len([e for e in all_errors if e['severity'] == 'ERROR']),
                'WARNING': len([e for e in all_errors if e['severity'] == 'WARNING'])
            }
        },
        'errors': all_errors
    }
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report


def main(
    start_from: int = 1,
    top_n_verbs: int = None,
    verbs_list: List[str] = None,
    validate_all: bool = False
):
    """
    Main validation function.
    
    Args:
        start_from: Position in verb list to start from (1-indexed)
        top_n_verbs: Number of verbs to validate from start_from position
        verbs_list: Specific list of verb names to validate
        validate_all: Validate all verbs in the dataset
    """
    # Load all verbs from CSV
    all_verbs = load_verbs_from_csv()
    
    # Select verbs based on parameters
    if validate_all:
        selected_verbs = all_verbs
    elif verbs_list:
        selected_verbs = [v for v in all_verbs if v['english'] in verbs_list]
        if len(selected_verbs) != len(verbs_list):
            found = {v['english'] for v in selected_verbs}
            missing = set(verbs_list) - found
            logger.warning(f"Some verbs not found in CSV: {missing}")
    else:
        start_idx = start_from - 1
        if top_n_verbs:
            end_idx = start_idx + top_n_verbs
            selected_verbs = all_verbs[start_idx:end_idx]
        else:
            selected_verbs = all_verbs[start_idx:]
    
    if not selected_verbs:
        logger.error("No verbs selected for validation")
        return
    
    logger.info(f"Validating {len(selected_verbs)} verbs")
    logger.info(f"Verbs: {', '.join(v['english'] for v in selected_verbs)}")
    
    # Set up paths
    base_dir = Path(__file__).parent.parent / "data" / "output" / "training_examples_for_verbs"
    output_dir = Path(__file__).parent.parent / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate all selected verbs
    all_errors = []
    for verb in selected_verbs:
        verb_english = verb['english']
        errors = validate_verb(verb_english, base_dir)
        all_errors.extend(errors)
    
    # Generate report
    if verbs_list:
        report_name = "validation_report_custom.json"
    elif validate_all:
        report_name = "validation_report_all.json"
    else:
        report_name = f"validation_report_{start_from}-{start_from + len(selected_verbs) - 1}.json"
    
    output_file = output_dir / report_name
    report = generate_validation_report(all_errors, output_file)
    
    # Print summary
    print("\n" + "="*80)
    print("VALIDATION REPORT")
    print("="*80)
    print(f"Verbs validated: {len(selected_verbs)}")
    print(f"Total errors found: {report['summary']['total_errors']}")
    print(f"\nErrors by severity:")
    for severity, count in report['summary']['errors_by_severity'].items():
        print(f"  {severity}: {count}")
    print(f"\nErrors by type:")
    for error_type, count in sorted(report['summary']['errors_by_type'].items(), key=lambda x: -x[1]):
        print(f"  {error_type}: {count}")
    print(f"\nDetailed report saved to: {output_file}")
    print("="*80)
    
    # Show first few errors
    if all_errors:
        print("\nSample errors (first 5):")
        for i, error in enumerate(all_errors[:5], 1):
            print(f"\n{i}. [{error['severity']}] {error['type']}")
            print(f"   File: {error['file']}")
            print(f"   {error['message']}")
    
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate training examples for consistency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate first 10 verbs
  python pipelines/validate_training_examples.py --top-n-verbs 10
  
  # Validate verbs 51-70
  python pipelines/validate_training_examples.py --start-from 51 --top-n-verbs 20
  
  # Validate specific verbs
  python pipelines/validate_training_examples.py --verbs "be,do,have,say"
  
  # Validate all verbs
  python pipelines/validate_training_examples.py --all
        """
    )
    
    parser.add_argument(
        "--start-from",
        type=int,
        default=1,
        help="Position in verb list to start from (1-indexed, default: 1)"
    )
    
    parser.add_argument(
        "--top-n-verbs",
        type=int,
        help="Number of verbs to validate from start position"
    )
    
    parser.add_argument(
        "--verbs",
        type=str,
        help="Comma-separated list of specific verbs to validate (e.g., 'be,do,have')"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all verbs in the dataset"
    )
    
    args = parser.parse_args()
    
    # Parse verbs list if provided
    verbs_list = None
    if args.verbs:
        verbs_list = [v.strip() for v in args.verbs.split(',')]
    
    main(
        start_from=args.start_from,
        top_n_verbs=args.top_n_verbs,
        verbs_list=verbs_list,
        validate_all=args.all
    )

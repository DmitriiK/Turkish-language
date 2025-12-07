#!/usr/bin/env python3
"""
Validate existing training examples for pronoun-verb consistency.

This script scans all training example JSON files and reports any that have
mismatches between the personal pronoun and the verb conjugation.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple
from grammer_metadata import TrainingExample


def load_example(file_path: Path) -> TrainingExample:
    """Load a training example from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return TrainingExample(**data)


def validate_all_examples(data_dir: Path) -> Tuple[List[Path], List[Tuple[Path, List[str]]]]:
    """Validate all training examples in the data directory.
    
    Args:
        data_dir: Path to the training examples directory
        
    Returns:
        Tuple of (valid_files, invalid_files_with_errors)
    """
    valid_files = []
    invalid_files = []
    
    # Find all JSON files
    json_files = list(data_dir.rglob("*.json"))
    total_files = len(json_files)
    
    print(f"Found {total_files} JSON files to validate...")
    print()
    
    for i, file_path in enumerate(json_files, 1):
        if i % 100 == 0:
            print(f"Progress: {i}/{total_files} files processed...")
        
        try:
            example = load_example(file_path)
            is_valid, errors = example.validate()
            
            if is_valid:
                valid_files.append(file_path)
            else:
                invalid_files.append((file_path, errors))
        except Exception as e:
            invalid_files.append((file_path, [f"Failed to load/validate: {str(e)}"]))
    
    return valid_files, invalid_files


def print_report(valid_files: List[Path], invalid_files: List[Tuple[Path, List[str]]]):
    """Print validation report."""
    total = len(valid_files) + len(invalid_files)
    
    print()
    print("=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)
    print()
    print(f"Total files: {total}")
    print(f"Valid files: {len(valid_files)} ({len(valid_files)/total*100:.1f}%)")
    print(f"Invalid files: {len(invalid_files)} ({len(invalid_files)/total*100:.1f}%)")
    print()
    
    if invalid_files:
        print("INVALID FILES:")
        print("-" * 80)
        for file_path, errors in invalid_files:
            print(f"\n❌ {file_path.relative_to(file_path.parents[3])}")
            for error in errors:
                print(f"   {error}")
        print()
        print("=" * 80)
    else:
        print("✅ All files are valid!")


def save_invalid_list(invalid_files: List[Tuple[Path, List[str]]], output_file: Path):
    """Save list of invalid files to a JSON file for further processing."""
    data = [
        {
            "file": str(file_path),
            "errors": errors
        }
        for file_path, errors in invalid_files
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Invalid files list saved to: {output_file}")


def main():
    """Main entry point."""
    # Default data directory
    script_dir = Path(__file__).parent
    default_data_dir = script_dir.parent / "data" / "output" / "training_examples_for_verbs"
    
    # Allow override via command line
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = default_data_dir
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)
    
    print(f"Scanning directory: {data_dir}")
    print()
    
    # Run validation
    valid_files, invalid_files = validate_all_examples(data_dir)
    
    # Print report
    print_report(valid_files, invalid_files)
    
    # Save invalid files list if any
    if invalid_files:
        output_file = script_dir.parent / "logs" / "invalid_examples.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        save_invalid_list(invalid_files, output_file)
        
        # Exit with error code
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

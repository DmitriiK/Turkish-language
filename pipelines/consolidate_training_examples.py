#!/usr/bin/env python3
"""
Consolidate training examples from individual JSON files into a single JSON file.

This script collects all training example JSON files for specified verbs and
consolidates them into a single JSON file containing a list of all examples.

Usage:
    python pipelines/consolidate_training_examples.py --start-from 1 --top-n-verbs 10
    python pipelines/consolidate_training_examples.py --verbs "be,do,have"
    python pipelines/consolidate_training_examples.py --start-from 51 --top-n-verbs 20 --output custom_output.json
"""

import argparse
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

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


def load_training_example(file_path: Path) -> Dict[str, Any]:
    """Load a single training example JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return None


def consolidate_examples_for_verb(verb_english: str, base_dir: Path) -> List[Dict[str, Any]]:
    """
    Consolidate all training examples for a single verb.
    
    Args:
        verb_english: English verb name (e.g., "be", "do", "say")
        base_dir: Base directory containing training examples
        
    Returns:
        List of training example dictionaries
    """
    # Find the verb directory (handle special characters in folder names)
    # Try exact match first, then try with underscores and escaped characters
    possible_patterns = [
        verb_english.replace(', ', ',_'),  # Replace comma-space with comma-underscore
        verb_english.replace(' ', '_'),  # Replace spaces with underscores
        verb_english,  # Exact match (try last to avoid partial matches)
    ]
    
    verb_dir = None
    for pattern in possible_patterns:
        # For exact match, check if directory name equals pattern exactly
        for candidate in base_dir.iterdir():
            if not candidate.is_dir():
                continue
            if candidate.name == pattern:
                verb_dir = candidate
                break
        
        # If not found, try glob pattern (for cases with additional suffixes)
        if not verb_dir:
            verb_dirs = list(base_dir.glob(f"{pattern}"))
            if verb_dirs:
                verb_dir = verb_dirs[0]
                break
    
    if not verb_dir:
        logger.warning(f"No directory found for verb: {verb_english}")
        return []
    
    examples = []
    
    # Load all JSON files in the verb directory
    json_files = sorted(verb_dir.glob("*.json"))
    
    logger.info(f"Loading {len(json_files)} examples for verb '{verb_english}' from {verb_dir.name}")
    
    for json_file in json_files:
        example = load_training_example(json_file)
        if example:
            examples.append(example)
    
    return examples


def consolidate_training_examples(
    verbs: List[Dict[str, Any]],
    base_dir: Path,
    output_file: Path
) -> Dict[str, Any]:
    """
    Consolidate training examples for multiple verbs into a single JSON file.
    
    Args:
        verbs: List of verb dictionaries from CSV
        base_dir: Base directory containing training examples
        output_file: Output file path for consolidated JSON
        
    Returns:
        Dictionary containing consolidated data
    """
    consolidated = {
        "metadata": {
            "total_verbs": len(verbs),
            "verbs": [v['english'] for v in verbs],
            "total_examples": 0
        },
        "examples": []
    }
    
    for verb in verbs:
        verb_english = verb['english']
        logger.info(f"Processing verb: {verb_english} (rank {verb['rank']})")
        
        examples = consolidate_examples_for_verb(verb_english, base_dir)
        consolidated["examples"].extend(examples)
        consolidated["metadata"]["total_examples"] += len(examples)
    
    # Write consolidated JSON
    logger.info(f"Writing {consolidated['metadata']['total_examples']} examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Successfully consolidated {consolidated['metadata']['total_examples']} examples for {len(verbs)} verbs")
    
    return consolidated


def main(
    start_from: int = 1,
    top_n_verbs: int = None,
    verbs_list: List[str] = None,
    output_file: str = None
):
    """
    Main function to consolidate training examples.
    
    Args:
        start_from: Position in verb list to start from (1-indexed)
        top_n_verbs: Number of verbs to process from start_from position
        verbs_list: Specific list of verb names to process
        output_file: Custom output file path
    """
    # Load all verbs from CSV
    all_verbs = load_verbs_from_csv()
    
    # Select verbs based on parameters
    if verbs_list:
        # Filter to only specified verbs
        selected_verbs = [v for v in all_verbs if v['english'] in verbs_list]
        if len(selected_verbs) != len(verbs_list):
            found = {v['english'] for v in selected_verbs}
            missing = set(verbs_list) - found
            logger.warning(f"Some verbs not found in CSV: {missing}")
    else:
        # Use start_from and top_n_verbs
        start_idx = start_from - 1  # Convert to 0-indexed
        
        if top_n_verbs:
            end_idx = start_idx + top_n_verbs
            selected_verbs = all_verbs[start_idx:end_idx]
        else:
            selected_verbs = all_verbs[start_idx:]
    
    if not selected_verbs:
        logger.error("No verbs selected for consolidation")
        return
    
    logger.info(f"Selected {len(selected_verbs)} verbs for consolidation")
    logger.info(f"Verbs: {', '.join(v['english'] for v in selected_verbs)}")
    
    # Set up paths
    base_dir = Path(__file__).parent.parent / "data" / "output" / "training_examples_for_verbs"
    
    if output_file:
        output_path = Path(output_file)
    else:
        # Generate default output filename
        if verbs_list:
            output_name = "consolidated_examples_custom.json"
        else:
            output_name = f"consolidated_examples_{start_from}-{start_from + len(selected_verbs) - 1}.json"
        
        output_path = Path(__file__).parent.parent / "data" / "output" / output_name
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Consolidate examples
    result = consolidate_training_examples(selected_verbs, base_dir, output_path)
    
    # Print summary
    print("\n" + "="*60)
    print("CONSOLIDATION SUMMARY")
    print("="*60)
    print(f"Total verbs processed: {result['metadata']['total_verbs']}")
    print(f"Total examples consolidated: {result['metadata']['total_examples']}")
    print(f"Average examples per verb: {result['metadata']['total_examples'] / result['metadata']['total_verbs']:.1f}")
    print(f"Output file: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Consolidate training examples into a single JSON file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consolidate first 10 verbs
  python pipelines/consolidate_training_examples.py --top-n-verbs 10
  
  # Consolidate verbs 51-70
  python pipelines/consolidate_training_examples.py --start-from 51 --top-n-verbs 20
  
  # Consolidate specific verbs
  python pipelines/consolidate_training_examples.py --verbs "be,do,have,say"
  
  # Consolidate with custom output file
  python pipelines/consolidate_training_examples.py --start-from 1 --top-n-verbs 50 --output my_examples.json
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
        help="Number of verbs to process from start position"
    )
    
    parser.add_argument(
        "--verbs",
        type=str,
        help="Comma-separated list of specific verbs to consolidate (e.g., 'be,do,have')"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Custom output file path (default: auto-generated based on verb range)"
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
        output_file=args.output
    )

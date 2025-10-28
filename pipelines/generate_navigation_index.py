#!/usr/bin/env python3
"""
Generate navigation index for Turkish verb learning app.
Scans all available training examples and creates a comprehensive navigation file.
"""

import json
from pathlib import Path
from typing import Dict, Any
import re


def scan_training_examples() -> Dict[str, Any]:
    """
    Scan all training example files and create navigation index.
    """
    base_path = Path(__file__).parent.parent / "data" / "output" / "training_examples_for_verbs"
    navigation_index = {
        "verbs": [],
        "verb_data": {}
    }
    
    print(f"Scanning directory: {base_path}")
    
    if not base_path.exists():
        print(f"Error: Directory {base_path} does not exist")
        return navigation_index
    
    # Scan all verb directories
    for verb_dir in sorted(base_path.iterdir()):
        if not verb_dir.is_dir() or verb_dir.name.startswith('.'):
            continue
            
        print(f"Processing verb directory: {verb_dir.name}")
        
        # Parse files in this verb directory
        verb_info = scan_verb_directory(verb_dir)
        
        if verb_info and verb_info["files"]:  # Only include verbs with actual files
            navigation_index["verbs"].append(verb_info["english_name"])
            navigation_index["verb_data"][verb_info["english_name"]] = verb_info
    
    return navigation_index


def scan_verb_directory(verb_dir: Path) -> Dict[str, Any]:
    """
    Scan a single verb directory and extract all available combinations.
    """
    verb_info = {
        "english_name": "",
        "turkish_infinitive": "",
        "folder_name": verb_dir.name,
        "tenses": {},
        "files": []
    }
    
    # Pattern to match file names: {pronoun}_{infinitive}_{tense}[_olumsuz].json
    # For compound verbs like "sahip_olmak", we need to match the tense properly
    # Tenses are: geniş_zaman, geçmiş_zaman, şimdiki_zaman
    # Polarity: optional _olumsuz suffix for negative
    file_pattern = re.compile(r'^(.+?)_(.+?)_(geniş_zaman|geçmiş_zaman|şimdiki_zaman)(_olumsuz)?\.json$')
    
    for file_path in verb_dir.glob("*.json"):
        if file_path.name.startswith('.'):
            continue
            
        match = file_pattern.match(file_path.name)
        if not match:
            print(f"  Warning: Could not parse file name: {file_path.name}")
            continue
            
        pronoun, infinitive, tense, polarity_suffix = match.groups()
        polarity = 'negative' if polarity_suffix == '_olumsuz' else 'positive'
        
        # Load the file to get metadata
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract verb information from the file
            if not verb_info["english_name"]:
                verb_info["english_name"] = data.get("verb_english", "")
                verb_info["turkish_infinitive"] = data.get("verb_infinitive", infinitive)
            
            # Create tense+polarity key for organizing files
            tense_polarity_key = f"{tense}_{polarity}"
            
            # Add tense+polarity information
            if tense_polarity_key not in verb_info["tenses"]:
                verb_info["tenses"][tense_polarity_key] = {
                    "tense": tense,
                    "polarity": polarity,
                    "pronouns": [],
                    "files": []
                }
            
            verb_info["tenses"][tense_polarity_key]["pronouns"].append(pronoun)
            verb_info["tenses"][tense_polarity_key]["files"].append({
                "pronoun": pronoun,
                "polarity": polarity,
                "file_path": f"data/output/training_examples_for_verbs/{verb_dir.name}/{file_path.name}",
                "relative_path": f"{verb_dir.name}/{file_path.name}"
            })
            
            # Add to overall files list
            verb_info["files"].append({
                "pronoun": pronoun,
                "tense": tense,
                "polarity": polarity,
                "infinitive": infinitive,
                "file_path": f"data/output/training_examples_for_verbs/{verb_dir.name}/{file_path.name}",
                "relative_path": f"{verb_dir.name}/{file_path.name}",
                "rank": data.get("verb_rank", 0)
            })
            
            print(f"  Found: {pronoun} + {infinitive} + {tense} ({polarity})")
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"  Error reading {file_path.name}: {e}")
            continue
    
    # Sort pronouns for consistent ordering
    for tense_info in verb_info["tenses"].values():
        tense_info["pronouns"] = sorted(list(set(tense_info["pronouns"])))
        tense_info["files"] = sorted(tense_info["files"], key=lambda x: x["pronoun"])
    
    verb_info["files"] = sorted(verb_info["files"], key=lambda x: (x["tense"], x["polarity"], x["pronoun"]))
    
    return verb_info


def save_navigation_index(navigation_index: Dict[str, Any]):
    """
    Save navigation index to JSON files for frontend use.
    """
    # Save to frontend public directory
    frontend_public = Path(__file__).parent.parent / "frontend" / "public" / "data"
    frontend_public.mkdir(parents=True, exist_ok=True)
    
    output_path = frontend_public / "navigation_index.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(navigation_index, f, indent=2, ensure_ascii=False)
    
    print(f"Navigation index saved to: {output_path}")
    
    # Also save a summary for debugging
    summary_path = frontend_public / "navigation_summary.json"
    summary = {
        "total_verbs": len(navigation_index["verbs"]),
        "verbs": []
    }
    
    for verb in navigation_index["verbs"]:
        verb_data = navigation_index["verb_data"][verb]
        summary["verbs"].append({
            "english": verb,
            "turkish": verb_data["turkish_infinitive"],
            "folder": verb_data["folder_name"],
            "tenses": list(verb_data["tenses"].keys()),
            "total_files": len(verb_data["files"])
        })
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"Navigation summary saved to: {summary_path}")
    
    return output_path


def main():
    """
    Main function to generate navigation index.
    """
    print("=== Turkish Verb Navigation Index Generator ===")
    
    # Scan all training examples
    navigation_index = scan_training_examples()
    
    print(f"\nFound {len(navigation_index['verbs'])} verbs with training data:")
    for verb in navigation_index["verbs"]:
        verb_data = navigation_index["verb_data"][verb]
        tense_count = len(verb_data["tenses"])
        file_count = len(verb_data["files"])
        print(f"  - {verb}: {tense_count} tenses, {file_count} files")
    
    # Save navigation index
    if navigation_index["verbs"]:
        output_path = save_navigation_index(navigation_index)
        print("\n✅ Navigation index generated successfully!")
        print(f"📁 Saved to: {output_path}")
    else:
        print("\n❌ No verbs found with training data")


if __name__ == "__main__":
    main()

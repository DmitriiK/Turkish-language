import csv
import json
import os
from pathlib import Path
from typing import List, Tuple, Optional

import toml
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from grammer_metadata import (
    VerbTense, PersonalPronoun, LanguageLevel, TrainingExample,
    VERB_FORM_INFOS
)

# Load environment variables
load_dotenv()


def load_config():
    """Load configuration from config.toml file."""
    try:
        # Look for config.toml in parent directory (project root)
        config_path = Path(__file__).parent.parent / "config.toml"
        config = toml.load(config_path)
        return config
    except FileNotFoundError:
        print("❌ Error: config.toml file not found")
        return None
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None


class VerbData:
    """Represents a verb from the CSV file"""
    def __init__(self, rank: int, english: str, russian: str, turkish: str):
        self.rank = rank
        self.english = english
        self.russian = russian
        self.turkish = turkish


def load_verbs_from_csv(file_path: str) -> List[VerbData]:
    """Parse verbs.csv and return list of VerbData objects"""
    verbs = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            rank = int(row['Rank'].strip())
            english = row[' English'].strip()
            russian = row[' Russian'].strip()
            turkish = row[' Turkish'].strip()
            verbs.append(VerbData(rank, english, russian, turkish))
    return verbs


def generate_combinations(
    verbs: List[VerbData],
    language_level: LanguageLevel
) -> List[Tuple[VerbData, VerbTense, Optional[PersonalPronoun]]]:
    """Generate combinations of verbs × tenses × pronouns for given level"""
    combinations = []

    # Filter verb forms by language level
    valid_verb_forms = [
        vf for vf in VERB_FORM_INFOS
        if vf.language_level.value <= language_level.value
    ]
    
    for verb in verbs:
        for verb_form in valid_verb_forms:
            # Handle pronouns based on verb form requirements
            if verb_form.type_of_personal_pronoun is None:
                # No personal pronouns (e.g., imperatives, participles)
                combinations.append((verb, verb_form.verb_tense, None))
            else:
                # Add all personal pronouns
                pronouns = [
                    PersonalPronoun.Ben, PersonalPronoun.Sen,
                    PersonalPronoun.O_Third, PersonalPronoun.Biz,
                    PersonalPronoun.Siz, PersonalPronoun.Onlar
                ]
                for pronoun in pronouns:
                    combinations.append((verb, verb_form.verb_tense, pronoun))
    
    return combinations


def load_prompt_template() -> str:
    """Load the prompt template with nested structure for comprehensive LLM structured output"""
    return """You are a Turkish language expert. Create a complete training example with nested Turkish verb structure following the exact format below.

Parameters:
- Verb (English): {verb_english}
- Verb (Turkish infinitive): {verb_infinitive}
- Tense: {verb_tense}
- Pronoun: {personal_pronoun}
- Level: {language_level}

EXAMPLE FORMAT (for reference):
For "to be" (olmak), şimdiki_zaman, ben, A1:
{{
  "verb_rank": 1,
  "verb_english": "to be",
  "verb_russian": "быть",
  "verb_infinitive": "olmak",
  "turkish_verb": {{
    "verb_full": "oluyorum",
    "root": "ol",
    "tense_affix": "uyor",
    "verb_tense": "şimdiki_zaman",
    "personal_pronoun": "ben",
    "personal_affix": "um"
  }},
  "language_level": "A1",
  "english_example_sentence": "I am becoming happy.",
  "russian_example_sentence": "Я становлюсь счастливым.",
  "turkish_example_sentence": "Ben mutlu oluyorum."
}}

REQUIREMENTS:
1. Correct Turkish verb conjugation following vowel harmony in the nested turkish_verb object
2. Natural example sentences in English, Russian, and Turkish (4-8 words each)
3. Use simple vocabulary appropriate for {language_level} level
4. Turkish sentence should use natural word order (SOV when appropriate)
5. All sentences should convey the same basic meaning
6. Fill ALL required fields including the nested turkish_verb structure

Generate a training example for the given parameters using this exact nested format."""


def generate_training_example(
    verb: VerbData,
    tense: VerbTense,
    pronoun: Optional[PersonalPronoun],
    prompt_template_str: str,
    language_level: LanguageLevel,
    config: dict
) -> Optional[TrainingExample]:
    """Generate a training example using LangChain with Azure OpenAI"""
    try:
        # Use Azure OpenAI
        azure_config = config['azure_model']
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Please set AZURE_OPENAI_API_KEY in your environment variables")
        
        llm = AzureChatOpenAI(
            api_key=api_key,
            api_version=azure_config['OPENAI_API_VERSION'],
            azure_endpoint=azure_config['AZURE_OPENAI_ENDPOINT'],
            model=azure_config['MODEL_NAME'],
            temperature=config['generation']['temperature'],
            max_tokens=config['generation']['max_output_tokens'],
        )
        
        # Use structured output with Pydantic model
        structured_llm = llm.with_structured_output(TrainingExample)
        
        # Create prompt template
        prompt = PromptTemplate(
            input_variables=[
                "verb_english", "verb_infinitive", "verb_tense",
                "personal_pronoun", "language_level"
            ],
            template=prompt_template_str
        )
        
        # Generate structured response
        chain = prompt | structured_llm
        
        # Prepare prompt inputs
        prompt_inputs = {
            "verb_english": verb.english,
            "verb_infinitive": verb.turkish,
            "verb_tense": tense.value,
            "personal_pronoun": pronoun.value if pronoun else "None",
            "language_level": language_level.value
        }
        
        # Generate structured response
        try:
            result = chain.invoke(prompt_inputs)
            
            # Check if structured output returned valid result
            if result is not None and hasattr(result, 'verb_english'):
                # Override verb_rank and verb_russian with actual values from CSV
                result.verb_rank = verb.rank
                result.verb_russian = verb.russian
                return result
            else:
                # Log raw response for debugging when structured output fails
                raw_chain = prompt | llm
                raw_response = raw_chain.invoke(prompt_inputs)
                print(f"🔍 Raw LLM response: {raw_response.content[:500]}...")
                
                raise ValueError(
                    "Structured output returned None - "
                    "model may have failed to generate proper response"
                )
                
        except Exception as generation_error:
            # Log raw response for debugging when generation fails
            try:
                raw_chain = prompt | llm
                raw_response = raw_chain.invoke(prompt_inputs)
                print(f"🔍 Raw LLM response on error: {raw_response.content[:500]}...")
            except Exception:
                print("🔍 Unable to get raw response for debugging")
            
            # Re-raise the original error
            raise generation_error
        
    except Exception as e:
        # Print error in red but don't stop the pipeline
        print(f"\n⚠️  SKIPPING VERB: {verb.english}")
        print(f"Error generating example for {verb.english} "
              f"({tense.value}, {pronoun})")
        print(f"Error details: {e}")
        print("Continuing with next combination...\n")
        return None  # Return None to indicate failure, but don't stop pipeline


def save_training_example(example: TrainingExample, output_dir: Path):
    """Save training example as JSON file with proper naming convention"""
    # Create folder structure: verb_english/ (without "to " prefix at the beginning)
    verb_name = example.verb_english
    if verb_name.startswith("to "):
        verb_name = verb_name[3:]  # Remove "to " from the beginning
    verb_name = verb_name.replace(" ", "_")
    verb_folder = output_dir / verb_name
    verb_folder.mkdir(parents=True, exist_ok=True)
    
    # Create filename: pronoun_infinitive_tense.json
    pronoun_part = (example.turkish_verb.personal_pronoun.value
                    if example.turkish_verb.personal_pronoun else "none")
    # Use the infinitive from the nested structure
    infinitive = example.verb_infinitive.replace(" ", "_")
    filename = (f"{pronoun_part}_{infinitive}_"
                f"{example.turkish_verb.verb_tense.value}.json")
    
    file_path = verb_folder / filename
    
    # Save as JSON (include computed property)
    json_data = example.model_dump()
    json_data['turkish_example_sentence_with_blank'] = example.turkish_example_sentence_with_blank
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=2)
    
    print(f"Saved: {file_path}")


def main(language_level: str = "A2", top_n_verbs: int = 10):
    """Main pipeline function
    
    Args:
        language_level: Target language level (A1, A2, B1, B2)
        top_n_verbs: Number of top verbs to process from the list
    """
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration. Exiting.")
        return
    
    # Display model information
    print(f"🤖 Using model: Azure OpenAI - {config['azure_model']['MODEL_NAME']}")
    print(f"🌡️  Temperature: {config['generation']['temperature']}")
    print("📊 Using nested TrainingExample structure")
    
    # Convert string to LanguageLevel enum
    level = LanguageLevel(language_level)
    print(f"Generating training examples for language level: {level}")
    print(f"Processing top {top_n_verbs} verbs from the list")
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    verbs_file = project_root / "data" / "input" / "verbs.csv"
    output_dir = (project_root / "data" / "output" /
                  "training_examples_for_verbs")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load verbs
    print("Loading verbs from CSV...")
    all_verbs = load_verbs_from_csv(str(verbs_file))
    
    # Limit to top N verbs
    verbs = all_verbs[:top_n_verbs]
    print(f"Loaded {len(all_verbs)} verbs, processing top {len(verbs)}")
    
    # Generate combinations
    print(f"Generating combinations for level {level}...")
    combinations = generate_combinations(verbs, level)
    print(f"Generated {len(combinations)} combinations")
    
    # Load prompt template
    print("Loading prompt template...")
    prompt_template = load_prompt_template()
    
    # Generate training examples
    print("Generating training examples...")
    generated_count = 0
    skipped_count = 0
    
    try:
        for i, (verb, tense, pronoun) in enumerate(combinations):
            print(f"Processing {i+1}/{len(combinations)}: {verb.english} "
                  f"({tense.value}, {pronoun})")
            
            example = generate_training_example(
                verb, tense, pronoun, prompt_template, level, config
            )
            
            # Skip if generation failed
            if example is None:
                skipped_count += 1
                continue
            # With fail-fast approach, example should never be None
            # But keeping this check for safety
            if example:
                save_training_example(example, output_dir)
                generated_count += 1
            else:
                print("❌ Unexpected: got None example without exception")
                break
        
        print(f"✅ Successfully generated {generated_count} training examples")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} examples due to generation failures")
        
    except Exception as e:
        print(f"\n❌ PIPELINE STOPPED due to error: {e}")
        print(f"Generated {generated_count} examples before failure.")
        raise e


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Turkish language training examples"
    )
    parser.add_argument(
        "--language-level",
        default="A2",
        choices=["A1", "A2", "B1", "B2"],
        help="Target language level (default: A2)"
    )
    parser.add_argument(
        "--top-n-verbs",
        type=int,
        default=10,
        help="Number of top verbs to process (default: 10)"
    )
    
    args = parser.parse_args()
    main(language_level=args.language_level, top_n_verbs=args.top_n_verbs)

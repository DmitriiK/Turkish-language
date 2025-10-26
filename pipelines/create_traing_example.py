import csv
import json
import os
import re
import time
from pathlib import Path
from typing import List, Tuple, Optional

import toml
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from grammer_metadata import (
    VerbTense, PersonalPronoun, LanguageLevel, TrainingExample,
    VERB_FORM_INFOS, VerbPolarity
)

# Load environment variables
load_dotenv()


class RateLimiter:
    """Simple rate limiter to control API requests per minute"""
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute  # seconds between requests
        self.last_request_time = 0.0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            print(f"   ⏳ Rate limit: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def handle_rate_limit_error(self, retry_delay: int = 60):
        """Handle rate limit error by waiting the specified delay"""
        print(f"   ⏸️  Rate limit exceeded, waiting {retry_delay}s before retry...")
        time.sleep(retry_delay)
        self.last_request_time = time.time()


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
) -> List[Tuple[VerbData, VerbTense, Optional[PersonalPronoun], VerbPolarity]]:
    """Generate combinations of verbs × tenses × pronouns × polarity for given level"""
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
                combinations.append((verb, verb_form.verb_tense, None, verb_form.polarity))
            else:
                # Add all personal pronouns
                pronouns = [
                    PersonalPronoun.Ben, PersonalPronoun.Sen,
                    PersonalPronoun.O_Third, PersonalPronoun.Biz,
                    PersonalPronoun.Siz, PersonalPronoun.Onlar
                ]
                for pronoun in pronouns:
                    combinations.append((verb, verb_form.verb_tense, pronoun, verb_form.polarity))
    
    return combinations


def load_prompt_template() -> str:
    """Load the prompt template from the prompt file"""
    prompt_file = Path(__file__).parent.parent / "prompts" / "create_training_example.prompt.md"
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_prompt_template_OLD() -> str:
    """OLD: Load the prompt template with nested structure for comprehensive LLM structured output"""
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
    polarity: VerbPolarity,
    prompt_template_str: str,
    language_level: LanguageLevel,
    config: dict,
    provider: str = "gemini",
    rate_limiter: Optional[RateLimiter] = None,
    max_retries: int = 3
) -> Tuple[Optional[TrainingExample], int, int]:
    """Generate a training example using LangChain with configurable LLM provider
    
    Args:
        verb: Verb data from CSV
        tense: Verb tense to use
        pronoun: Personal pronoun (optional)
        polarity: Verb polarity (positive/negative)
        prompt_template_str: Prompt template string
        language_level: Language level for examples
        config: Configuration dictionary
        provider: LLM provider to use ("gemini" or "azure")
        rate_limiter: Optional rate limiter to control request frequency
        max_retries: Maximum number of retries on rate limit errors
    
    Returns:
        Tuple of (TrainingExample or None, prompt_tokens, completion_tokens)
    """
    
    def extract_retry_delay(error_message: str) -> int:
        """Extract retry delay in seconds from error message
        
        Parses error messages like:
        retry_delay { seconds: 23 }
        
        Returns:
            Retry delay in seconds, or 60 as default
        """
        match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', str(error_message))
        if match:
            return int(match.group(1))
        return 60  # Default to 60 seconds if can't parse
    
    # Retry loop
    for attempt in range(max_retries + 1):
        try:
            # Apply rate limiting if configured
            if rate_limiter:
                rate_limiter.wait_if_needed()
            
            # Initialize LLM based on provider
            if provider == "azure":
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
                    max_retries=0,  # Don't retry on rate limits - we handle it
                )
            else:  # gemini
                # Use Google Gemini
                api_key = os.getenv('GEMINI_API_KEY')
                if not api_key:
                    raise ValueError("Please set GEMINI_API_KEY in your environment variables")
                
                llm = ChatGoogleGenerativeAI(
                    model=config['model']['name'],
                    google_api_key=api_key,
                    temperature=config['generation']['temperature'],
                    max_output_tokens=config['generation']['max_output_tokens'],
                    max_retries=0,  # Don't retry on rate limits - we handle it
                )
            
            # Use structured output with Pydantic model
            structured_llm = llm.with_structured_output(TrainingExample)
            
            # Create prompt template
            prompt = PromptTemplate(
                input_variables=[
                    "verb_english", "verb_infinitive", "verb_tense",
                    "personal_pronoun", "language_level", "polarity"
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
                "language_level": language_level.value,
                "polarity": polarity.value
            }
            
            # Generate structured response
            try:
                # Log prompt size BEFORE making API call
                formatted_prompt = prompt.format(**prompt_inputs)
                prompt_char_count = len(formatted_prompt)
                estimated_tokens = prompt_char_count // 4  # Rough estimate: 1 token ≈ 4 chars
                print(f"   📝 Prompt size: {prompt_char_count} chars (~{estimated_tokens} tokens estimated)")
                
                # Make a single call that gives us both structured output and metadata
                # Use the base LLM first to get full response with metadata
                raw_chain = prompt | llm
                raw_response = raw_chain.invoke(prompt_inputs)
                
                # Get token usage from response metadata
                prompt_tokens = 0
                completion_tokens = 0
                
                # Try different metadata formats (Azure vs Gemini)
                if hasattr(raw_response, 'usage_metadata') and raw_response.usage_metadata:
                    # Gemini format
                    usage = raw_response.usage_metadata
                    prompt_tokens = usage.get('input_tokens', 0)
                    completion_tokens = usage.get('output_tokens', 0)
                    print(f"   📊 Tokens: {prompt_tokens} input + {completion_tokens} output = {prompt_tokens + completion_tokens} total")
                elif hasattr(raw_response, 'response_metadata'):
                    # Azure format
                    token_usage = raw_response.response_metadata.get('token_usage', {})
                    prompt_tokens = token_usage.get('prompt_tokens', 0)
                    completion_tokens = token_usage.get('completion_tokens', 0)
                    print(f"   📊 Tokens: {prompt_tokens} input + {completion_tokens} output = {prompt_tokens + completion_tokens} total")
                
                # Now get structured output (this uses cached response, shouldn't count tokens again)
                    # Now get structured output (this uses cached response, shouldn't count tokens again)
                result = chain.invoke(prompt_inputs)
                
                # Check if structured output returned valid result
                if result is not None and hasattr(result, 'verb_english'):
                    # Override verb_rank and verb_russian with actual values from CSV
                    result.verb_rank = verb.rank
                    result.verb_russian = verb.russian
                    
                    return result, prompt_tokens, completion_tokens
                else:
                    raise ValueError(
                        "Structured output returned None - "
                        "model may have failed to generate proper response"
                    )
                    
            except Exception as generation_error:
                # Check if this is a rate limit error (429)
                error_str = str(generation_error)
                if '429' in error_str or 'RateLimitReached' in error_str or 'rate limit' in error_str.lower():
                    if attempt < max_retries:
                        # Extract retry delay from error message
                        retry_delay = extract_retry_delay(error_str)
                        print(f"   ⚠️  Rate limit hit (attempt {attempt + 1}/{max_retries + 1})")
                        
                        # Use rate limiter to wait for the specified delay
                        if rate_limiter:
                            rate_limiter.handle_rate_limit_error(retry_delay)
                        else:
                            print(f"   ⏳ Waiting {retry_delay}s before retry...")
                            time.sleep(retry_delay)
                        
                        # Continue to next retry attempt
                        continue
                    else:
                        # Max retries reached
                        print(f"   ❌ Max retries ({max_retries}) reached for rate limit")
                        raise generation_error
                else:
                    # Not a rate limit error, print and re-raise
                    print(f"   ❌ Generation error: {str(generation_error)[:200]}")
                    raise generation_error
            
        except Exception as outer_error:
            # Catch errors from LLM initialization or other setup
            error_str = str(outer_error)
            if '429' in error_str or 'RateLimitReached' in error_str or 'rate limit' in error_str.lower():
                if attempt < max_retries:
                    # Extract retry delay from error message
                    retry_delay = extract_retry_delay(error_str)
                    print(f"   ⚠️  Rate limit hit during setup (attempt {attempt + 1}/{max_retries + 1})")
                    
                    # Use rate limiter to wait for the specified delay
                    if rate_limiter:
                        rate_limiter.handle_rate_limit_error(retry_delay)
                    else:
                        print(f"   ⏳ Waiting {retry_delay}s before retry...")
                        time.sleep(retry_delay)
                    
                    # Continue to next retry attempt
                    continue
                else:
                    # Max retries reached
                    print(f"   ❌ Max retries ({max_retries}) reached")
                    # Fall through to final error handling
            
            # Not a rate limit error or max retries reached
            # Print error but don't stop the pipeline
            print(f"\n⚠️  SKIPPING VERB: {verb.english}")
            print(f"Error generating example for {verb.english} "
                  f"({tense.value}, {pronoun})")
            print(f"Error details: {outer_error}")
            print("Continuing with next combination...\n")
            return None, 0, 0  # Return None and 0 tokens to indicate failure
    
    # Should never reach here
    return None, 0, 0


def save_training_example(example: TrainingExample, output_dir: Path, polarity: VerbPolarity):
    """Save training example as JSON file with proper naming convention"""
    # Create folder structure: verb_english/ (without "to " prefix at the beginning)
    verb_name = example.verb_english
    if verb_name.startswith("to "):
        verb_name = verb_name[3:]  # Remove "to " from the beginning
    verb_name = verb_name.replace(" ", "_")
    verb_folder = output_dir / verb_name
    verb_folder.mkdir(parents=True, exist_ok=True)
    
    # Create filename: pronoun_infinitive_tense_polarity.json
    pronoun_part = (example.turkish_verb.personal_pronoun.value
                    if example.turkish_verb.personal_pronoun else "none")
    # Use the infinitive from the nested structure
    infinitive = example.verb_infinitive.replace(" ", "_")
    # Use Turkish terms: no suffix for positive, _olumsuz for negative
    polarity_suffix = "_olumsuz" if polarity == VerbPolarity.Negative else ""
    filename = (f"{pronoun_part}_{infinitive}_"
                f"{example.turkish_verb.verb_tense.value}{polarity_suffix}.json")
    
    file_path = verb_folder / filename
    
    # Save as JSON (include computed property)
    json_data = example.model_dump()
    json_data['turkish_example_sentence_with_blank'] = example.turkish_example_sentence_with_blank
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=2)
    
    print(f"Saved: {file_path}")


def main(
    language_level: str = "A2",
    top_n_verbs: Optional[int] = None,
    specific_verbs: Optional[List[str]] = None,
    tenses: Optional[List[str]] = None,
    pronouns: Optional[List[str]] = None,
    polarities: Optional[List[str]] = None,
    provider: Optional[str] = None
):
    """Main pipeline function
    
    Args:
        language_level: Target language level (A1, A2, B1, B2)
        top_n_verbs: Number of top verbs to process from the list
        specific_verbs: List of specific verb names (English) to process
        tenses: List of specific tenses to generate (None = all). Values: şimdiki_zaman, geçmiş_zaman, geniş_zaman
        pronouns: List of specific pronouns to generate (None = all). Values: ben, sen, o, biz, siz, onlar
        polarities: List of specific polarities to generate (None = all). Values: positive, negative
        provider: LLM provider to use ("gemini" or "azure"). If None, uses default from config
    """
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration. Exiting.")
        return
    
    # Determine provider
    if provider is None:
        provider = config.get('provider', {}).get('default', 'gemini')
    
    # Ensure provider is valid
    assert provider in ['gemini', 'azure'], f"Invalid provider: {provider}. Must be 'gemini' or 'azure'"
    
    # Display model information
    if provider == "azure":
        print(f"🤖 Using model: Azure OpenAI - {config['azure_model']['MODEL_NAME']}")
    else:
        print(f"🤖 Using model: Google Gemini - {config['model']['name']}")
    print(f"🌡️  Temperature: {config['generation']['temperature']}")
    print("📊 Using nested TrainingExample structure")
    
    # Set up rate limiter
    rate_limits = config.get('rate_limits', {})
    requests_per_minute = rate_limits.get(provider, 60)  # default to 60 if not specified
    rate_limiter = RateLimiter(requests_per_minute)
    print(f"⏱️  Rate limit: {requests_per_minute} requests/minute ({60.0/requests_per_minute:.1f}s between requests)")
    
    # Convert string to LanguageLevel enum
    level = LanguageLevel(language_level)
    print(f"Generating training examples for language level: {level}")
    
    if specific_verbs:
        print(f"Processing specific verbs: {', '.join(specific_verbs)}")
    else:
        if top_n_verbs is None:
            top_n_verbs = 10
        print(f"Processing top {top_n_verbs} verbs from the list")
    
    # Display filters if any
    if tenses:
        print(f"🎯 Filtering tenses: {', '.join(tenses)}")
    if pronouns:
        print(f"🎯 Filtering pronouns: {', '.join(pronouns)}")
    if polarities:
        print(f"🎯 Filtering polarities: {', '.join(polarities)}")
    
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
    
    # Filter verbs based on parameters
    if specific_verbs:
        # Filter to only the specified verbs
        verbs = [v for v in all_verbs if v.english in specific_verbs]
        if len(verbs) != len(specific_verbs):
            found_verbs = {v.english for v in verbs}
            missing = set(specific_verbs) - found_verbs
            print(f"⚠️  Warning: Could not find verbs: {', '.join(missing)}")
        print(f"Loaded {len(all_verbs)} verbs, processing {len(verbs)} specific verbs")
    else:
        # Limit to top N verbs
        verbs = all_verbs[:top_n_verbs]
        print(f"Loaded {len(all_verbs)} verbs, processing top {len(verbs)}")
    
    # Generate combinations
    print(f"Generating combinations for level {level}...")
    all_combinations = generate_combinations(verbs, level)
    
    # Filter combinations based on tenses, pronouns, and polarities
    filtered_combinations = []
    for verb, tense, pronoun, polarity in all_combinations:
        # Filter by tense
        if tenses and tense.value not in tenses:
            continue
        # Filter by pronoun
        if pronouns and pronoun.value not in pronouns:
            continue
        # Filter by polarity
        if polarities and polarity.value not in polarities:
            continue
        filtered_combinations.append((verb, tense, pronoun, polarity))
    
    combinations = filtered_combinations
    print(f"Generated {len(combinations)} combinations (after filtering)")
    
    # Load prompt template
    print("Loading prompt template...")
    prompt_template = load_prompt_template()
    
    # Generate training examples
    print("Generating training examples...")
    generated_count = 0
    skipped_count = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    # Track per-verb statistics
    current_verb = None
    verb_prompt_tokens = 0
    verb_completion_tokens = 0
    verb_example_count = 0
    
    try:
        for i, (verb, tense, pronoun, polarity) in enumerate(combinations):
            # Check if we're starting a new verb
            if current_verb is None:
                current_verb = verb.english
            elif current_verb != verb.english:
                # Print statistics for the previous verb
                verb_total = verb_prompt_tokens + verb_completion_tokens
                print(f"\n   📊 Verb '{current_verb}' complete: {verb_example_count} examples, "
                      f"{verb_total:,} tokens ({verb_prompt_tokens:,} in + {verb_completion_tokens:,} out)")
                # Reset for new verb
                current_verb = verb.english
                verb_prompt_tokens = 0
                verb_completion_tokens = 0
                verb_example_count = 0
            
            polarity_str = polarity.value
            print(f"\nProcessing {i+1}/{len(combinations)}: {verb.english} "
                  f"({tense.value}, {pronoun}, {polarity_str})")
            
            example, prompt_tokens, completion_tokens = generate_training_example(
                verb, tense, pronoun, polarity, prompt_template, level, config, provider, rate_limiter
            )
            
            # Track token usage (total and per-verb)
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            verb_prompt_tokens += prompt_tokens
            verb_completion_tokens += completion_tokens
            
            # Skip if generation failed
            if example is None:
                skipped_count += 1
                continue
            # With fail-fast approach, example should never be None
            # But keeping this check for safety
            if example:
                save_training_example(example, output_dir, polarity)
                generated_count += 1
                verb_example_count += 1
                
                # Show token count for this example and cumulative total
                example_total = prompt_tokens + completion_tokens
                cumulative_total = total_prompt_tokens + total_completion_tokens
                print(f"   ✅ Saved ({example_total:,} tokens | cumulative: {cumulative_total:,} tokens)")
            else:
                print("❌ Unexpected: got None example without exception")
                break
        
        # Print statistics for the last verb
        if current_verb and verb_example_count > 0:
            verb_total = verb_prompt_tokens + verb_completion_tokens
            print(f"\n   📊 Verb '{current_verb}' complete: {verb_example_count} examples, "
                  f"{verb_total:,} tokens ({verb_prompt_tokens:,} in + {verb_completion_tokens:,} out)")
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully generated {generated_count} training examples")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} examples due to generation failures")
        
        # Display token usage summary
        total_tokens = total_prompt_tokens + total_completion_tokens
        print(f"\n📊 Token Usage Summary:")
        print(f"   Input tokens (prompt):      {total_prompt_tokens:,}")
        print(f"   Output tokens (completion): {total_completion_tokens:,}")
        print(f"   Total tokens:               {total_tokens:,}")
        print(f"   Average per example:        {total_tokens // generated_count if generated_count > 0 else 0:,}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ PIPELINE STOPPED due to error: {e}")
        print(f"Generated {generated_count} examples before failure.")
        total_tokens = total_prompt_tokens + total_completion_tokens
        print(f"\n📊 Token Usage (until failure):")
        print(f"   Input tokens:  {total_prompt_tokens:,}")
        print(f"   Output tokens: {total_completion_tokens:,}")
        print(f"   Total tokens:  {total_tokens:,}")
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
        default=None,
        help="Number of top verbs to process (default: 10 if no --verbs specified)"
    )
    parser.add_argument(
        "--verbs",
        type=str,
        nargs="+",
        help='Specific verbs to process (e.g., --verbs "to be" "to do" "to go")'
    )
    parser.add_argument(
        "--tenses",
        type=str,
        nargs="+",
        choices=["şimdiki_zaman", "geçmiş_zaman", "geniş_zaman"],
        help='Specific tenses to generate (e.g., --tenses şimdiki_zaman geçmiş_zaman)'
    )
    parser.add_argument(
        "--pronouns",
        type=str,
        nargs="+",
        choices=["ben", "sen", "o", "biz", "siz", "onlar"],
        help='Specific pronouns to generate (e.g., --pronouns ben sen)'
    )
    parser.add_argument(
        "--polarities",
        type=str,
        nargs="+",
        choices=["positive", "negative"],
        help='Specific polarities to generate (e.g., --polarities positive)'
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["gemini", "azure"],
        default=None,
        help='LLM provider to use: "gemini" or "azure" (default: uses config.toml setting)'
    )
    
    args = parser.parse_args()
    
    # If specific verbs are provided, use them; otherwise use top-n
    if args.verbs:
        main(
            language_level=args.language_level,
            specific_verbs=args.verbs,
            tenses=args.tenses,
            pronouns=args.pronouns,
            polarities=args.polarities,
            provider=args.provider
        )
    else:
        top_n = args.top_n_verbs if args.top_n_verbs else 10
        main(
            language_level=args.language_level,
            top_n_verbs=top_n,
            tenses=args.tenses,
            pronouns=args.pronouns,
            polarities=args.polarities,
            provider=args.provider
        )

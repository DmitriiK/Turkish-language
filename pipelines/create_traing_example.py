import csv
import json
import os
import re
import time
import atexit
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Any, Dict

import toml
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from grammer_metadata import (
    VerbTense, PersonalPronoun, LanguageLevel, TrainingExample,
    VERB_FORM_INFOS, VerbPolarity
)

# Load environment variables
load_dotenv()


# Global logger state
class PipelineLogger:
    """Logger for pipeline execution with automatic cleanup on exit"""
    def __init__(self):
        self.log_file = None
        self.start_time = None
        self.generated_count = 0
        self.skipped_count = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.processed_verbs = set()
        self.args = None
        self.model_name = None
        self.interrupted = False
        self.error_message = None
        self.file_durations = []  # Track duration for each file creation
        self.error_info = None  # Store error information if pipeline fails
        
    def initialize(self, log_dir: Path, args: Dict[str, Any], model_name: str):
        """Initialize logger with log file"""
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"pipeline_log_{timestamp}.txt"
        self.start_time = datetime.now()
        self.args = args
        self.model_name = model_name
        
        # Register cleanup handler
        atexit.register(self.write_final_log)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Write initial log
        self._write_start_log()
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.interrupted = True
        self.error_message = f"Pipeline interrupted by signal {signum}"
        print("\n⚠️  Pipeline interrupted. Writing final log...")
        self.write_final_log()
        sys.exit(1)
    
    def _write_start_log(self):
        """Write pipeline start information"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("TURKISH LANGUAGE TRAINING PIPELINE LOG\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {self.model_name}\n\n")
            f.write("Input Arguments:\n")
            for key, value in self.args.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n" + "=" * 80 + "\n\n")
    
    def update_stats(self, prompt_tokens: int, completion_tokens: int, verb_english: str,
                     duration: float, generated: bool = True):
        """Update statistics during processing
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            verb_english: English name of the verb
            duration: Time taken to generate this file in seconds
            generated: Whether file was generated (True) or skipped (False)
        """
        if prompt_tokens == 0 and completion_tokens == 0:
            raise ValueError(
                "Token counts are zero - unable to get actual token usage from LLM. "
                "Pipeline requires accurate token tracking."
            )
        
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.processed_verbs.add(verb_english)
        self.file_durations.append(duration)
        if generated:
            self.generated_count += 1
        else:
            self.skipped_count += 1
    
    def increment_skipped(self):
        """Increment skipped count"""
        self.skipped_count += 1
    
    def mark_interrupted(self):
        """Mark pipeline as interrupted"""
        self.interrupted = True
    
    def set_error(self, error: Exception):
        """Store error information"""
        import traceback
        self.error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc()
        }
    
    def write_verb_summary(self, verb_english: str, files_created: int,
                           prompt_tokens: int, completion_tokens: int):
        """Write intermediate summary for each verb"""
        if self.log_file is None:
            return
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                total_tokens = prompt_tokens + completion_tokens
                f.write(f"Verb: {verb_english}\n")
                f.write(f"  Files Created: {files_created}\n")
                f.write(f"  Tokens Used: {total_tokens:,} ({prompt_tokens:,} in + {completion_tokens:,} out)\n")
                f.write("\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not write verb summary: {e}")
    
    def write_final_log(self):
        """Write final statistics (called on exit)"""
        if self.log_file is None or self.start_time is None:
            return
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write("PIPELINE EXECUTION SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                
                if self.error_info:
                    f.write("Status: FAILED\n\n")
                elif self.interrupted:
                    f.write("Status: INTERRUPTED BY USER\n\n")
                else:
                    f.write("Status: COMPLETED\n\n")
                
                f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {duration}\n\n")
                
                f.write("Statistics:\n")
                f.write(f"  Processed Verbs: {len(self.processed_verbs)}\n")
                f.write(f"  Created Files: {self.generated_count}\n")
                f.write(f"  Skipped Files: {self.skipped_count}\n\n")
                
                f.write("Token Usage:\n")
                f.write(f"  Input Tokens (Prompt): {self.total_prompt_tokens:,}\n")
                f.write(f"  Output Tokens (Completion): {self.total_completion_tokens:,}\n")
                f.write(f"  Total Tokens: {self.total_prompt_tokens + self.total_completion_tokens:,}\n")
                
                if self.generated_count > 0:
                    avg_tokens = (self.total_prompt_tokens + self.total_completion_tokens) // self.generated_count
                    f.write(f"  Average Tokens per File: {avg_tokens:,}\n\n")
                else:
                    f.write("\n")
                
                f.write("Performance:\n")
                if self.file_durations:
                    avg_duration = sum(self.file_durations) / len(self.file_durations)
                    min_duration = min(self.file_durations)
                    max_duration = max(self.file_durations)
                    f.write(f"  Average File Generation Time: {avg_duration:.2f}s\n")
                    f.write(f"  Min File Generation Time: {min_duration:.2f}s\n")
                    f.write(f"  Max File Generation Time: {max_duration:.2f}s\n")
                else:
                    f.write(f"  No files generated\n")
                
                f.write("\n" + "=" * 80 + "\n")
                
                if self.processed_verbs:
                    f.write("\nProcessed Verbs:\n")
                    for verb in sorted(self.processed_verbs):
                        f.write(f"  - {verb}\n")
                
                # Write error information if pipeline failed
                if self.error_info:
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("ERROR INFORMATION\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(f"Error Type: {self.error_info['type']}\n")
                    f.write(f"Error Message: {self.error_info['message']}\n\n")
                    f.write("Traceback:\n")
                    f.write(self.error_info['traceback'])
                
                f.write("\n" + "=" * 80 + "\n")
        except Exception as e:
            # If we can't write the final log, at least try to print it
            print(f"\n⚠️  Warning: Could not write final log: {e}")

# Global logger instance
pipeline_logger = PipelineLogger()


class TokenUsageCallback(BaseCallbackHandler):
    """Callback to capture token usage from LLM responses"""
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Capture token usage when LLM call completes"""
        # Try multiple ways to extract token usage
        if response.llm_output:
            # OpenAI format
            if 'token_usage' in response.llm_output:
                usage = response.llm_output['token_usage']
                self.prompt_tokens = usage.get('prompt_tokens', 0)
                self.completion_tokens = usage.get('completion_tokens', 0)
                self.total_tokens = usage.get('total_tokens', 0)
            # Gemini format (usage_metadata)
            elif 'usage_metadata' in response.llm_output:
                usage = response.llm_output['usage_metadata']
                self.prompt_tokens = usage.get('prompt_token_count', 0) or usage.get('input_tokens', 0)
                self.completion_tokens = usage.get('candidates_token_count', 0) or usage.get('output_tokens', 0)
                self.total_tokens = usage.get('total_token_count', 0) or (self.prompt_tokens + self.completion_tokens)
        
        # Also check in generations metadata
        if self.prompt_tokens == 0 and response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, 'generation_info') and gen.generation_info:
                        if 'usage_metadata' in gen.generation_info:
                            usage = gen.generation_info['usage_metadata']
                            self.prompt_tokens = usage.get('prompt_token_count', 0)
                            self.completion_tokens = usage.get('candidates_token_count', 0)
                            self.total_tokens = usage.get('total_token_count', 0)
                            break
    
    def reset(self):
        """Reset token counters"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0


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
            else:  # gemini (AI Studio API)
                # Use Google Gemini AI Studio API
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
                # Create callback to capture token usage from the base LLM call
                token_callback = TokenUsageCallback()
                
                # Configure callbacks for BOTH the base LLM and structured wrapper
                config_with_callbacks = {"callbacks": [token_callback]}
                
                # Use structured chain with callback
                result = chain.invoke(prompt_inputs, config=config_with_callbacks)
                
                # Get token usage from callback
                prompt_tokens = token_callback.prompt_tokens
                completion_tokens = token_callback.completion_tokens
                
                # FAIL if we don't have accurate token counts
                if prompt_tokens == 0 or completion_tokens == 0:
                    raise ValueError(
                        f"Failed to capture accurate token usage from LLM response. "
                        f"Got prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}. "
                        f"Pipeline requires accurate token tracking and will not use estimates."
                    )
                
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
                
                # Check for daily quota limit - this is fatal and should not retry
                if 'GenerateRequestsPerDayPerProjectPerModel' in error_str or \
                   'generate_requests_per_model_per_day' in error_str.lower():
                    print(f"   ❌ FATAL: Daily quota limit reached!")
                    print(f"   📊 You've hit the Gemini API daily quota limit.")
                    print(f"   💡 Wait 24 hours or upgrade to paid tier for higher limits.")
                    # Re-raise as fatal error to stop the pipeline
                    raise RuntimeError(
                        "Daily quota limit reached. Cannot continue. "
                        "Wait 24 hours or upgrade to paid tier."
                    ) from generation_error
                
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
            
            # Check for daily quota limit - this is fatal and should not retry
            if 'GenerateRequestsPerDayPerProjectPerModel' in error_str or \
               'generate_requests_per_model_per_day' in error_str.lower():
                print("   ❌ FATAL: Daily quota limit reached!")
                print("   📊 You've hit the Gemini API daily quota limit.")
                print("   💡 Wait 24 hours or upgrade to paid tier for higher limits.")
                # Re-raise as fatal error to stop the pipeline
                raise RuntimeError(
                    "Daily quota limit reached. Cannot continue. "
                    "Wait 24 hours or upgrade to paid tier."
                ) from outer_error
            
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
            # Check if this is a daily quota error - if so, re-raise to stop pipeline
            if isinstance(outer_error, RuntimeError) and 'Daily quota limit' in str(outer_error):
                print("\n❌ FATAL ERROR: Daily quota limit reached. Stopping pipeline.")
                raise outer_error
            
            # Print error but don't stop the pipeline for other errors
            print(f"\n⚠️  SKIPPING VERB: {verb.english}")
            print(f"Error generating example for {verb.english} "
                  f"({tense.value}, {pronoun})")
            print(f"Error details: {outer_error}")
            print("Continuing with next combination...\n")
            return None, 0, 0  # Return None and 0 tokens to indicate failure
    
    # Should never reach here
    return None, 0, 0


def save_training_example(example: TrainingExample, output_dir: Path, polarity: VerbPolarity) -> Path:
    """Save training example as JSON file with proper naming convention
    
    Returns:
        Path: The path to the saved file
    """
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
    
    return file_path


def check_example_exists(verb: VerbData, tense: VerbTense, pronoun: Optional[PersonalPronoun],
                         polarity: VerbPolarity, output_dir: Path) -> bool:
    """Check if a training example file already exists"""
    # Create the same path structure as save_training_example
    verb_name = verb.english
    if verb_name.startswith("to "):
        verb_name = verb_name[3:]
    verb_name = verb_name.replace(" ", "_")
    verb_folder = output_dir / verb_name
    
    # Create filename
    pronoun_part = pronoun.value if pronoun else "none"
    infinitive = verb.turkish.replace(" ", "_")
    polarity_suffix = "_olumsuz" if polarity == VerbPolarity.Negative else ""
    filename = f"{pronoun_part}_{infinitive}_{tense.value}{polarity_suffix}.json"
    
    file_path = verb_folder / filename
    return file_path.exists()


def main(
    language_level: str = "A2",
    top_n_verbs: Optional[int] = None,
    specific_verbs: Optional[List[str]] = None,
    tenses: Optional[List[str]] = None,
    pronouns: Optional[List[str]] = None,
    polarities: Optional[List[str]] = None,
    provider: Optional[str] = None,
    skip_existing: bool = False
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
        skip_existing: If True, skip combinations that already have generated files
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
    
    # Get model name for logging
    if provider == "azure":
        model_name = f"Azure OpenAI - {config['azure_model']['MODEL_NAME']}"
    else:
        model_name = f"Google Gemini - {config['model']['name']}"
    
    # Initialize logger
    project_root = Path(__file__).parent.parent
    log_dir = project_root / "logs"
    
    logger_args = {
        "language_level": language_level,
        "top_n_verbs": top_n_verbs,
        "specific_verbs": specific_verbs,
        "tenses": tenses,
        "pronouns": pronouns,
        "polarities": polarities,
        "provider": provider,
        "skip_existing": skip_existing,
        "temperature": config['generation']['temperature']
    }
    
    pipeline_logger.initialize(log_dir, logger_args, model_name)
    print(f"📝 Logging to: {pipeline_logger.log_file}")
    
    # Display model information
    print(f"🤖 Using model: {model_name}")
    print(f"🌡️  Temperature: {config['generation']['temperature']}")
    print("📊 Using nested TrainingExample structure")
    
    # Set up rate limiter
    rate_limits = config.get('rate_limits', {})
    requests_per_minute = rate_limits.get(provider, 60)  # default to 60 if not specified
    rate_limiter = RateLimiter(requests_per_minute)
    print(f"⏱️  Rate limit: {requests_per_minute} requests/minute ({60.0/requests_per_minute:.1f}s between requests)")
    
    # Display skip-existing setting
    if skip_existing:
        print("⏭️  Mode: Skip existing files")
    
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
                # Write verb summary to log
                pipeline_logger.write_verb_summary(current_verb, verb_example_count,
                                                   verb_prompt_tokens, verb_completion_tokens)
                # Reset for new verb
                current_verb = verb.english
                verb_prompt_tokens = 0
                verb_completion_tokens = 0
                verb_example_count = 0
            
            polarity_str = polarity.value
            print(f"\nProcessing {i+1}/{len(combinations)}: {verb.english} "
                  f"({tense.value}, {pronoun}, {polarity_str})")
            
            # Check if file already exists and skip if requested
            if skip_existing and check_example_exists(verb, tense, pronoun, polarity, output_dir):
                print("   ⏭️  Skipping (file already exists)")
                skipped_count += 1
                pipeline_logger.increment_skipped()
                continue
            
            # Track time for this file generation
            file_start_time = time.time()
            
            example, prompt_tokens, completion_tokens = generate_training_example(
                verb, tense, pronoun, polarity, prompt_template, level, config, provider, rate_limiter
            )
            
            file_duration = time.time() - file_start_time
            
            # Track token usage (total and per-verb)
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            verb_prompt_tokens += prompt_tokens
            verb_completion_tokens += completion_tokens
            
            # Skip if generation failed
            if example is None:
                skipped_count += 1
                pipeline_logger.increment_skipped()
                continue
            # With fail-fast approach, example should never be None
            # But keeping this check for safety
            if example:
                file_path = save_training_example(example, output_dir, polarity)
                total_tokens = prompt_tokens + completion_tokens
                cumulative = total_prompt_tokens + total_completion_tokens
                print(f"   ✅ Saved to: {file_path}")
                print(f"      ({total_tokens:,} tokens | {file_duration:.2f}s | "
                      f"cumulative: {cumulative:,} tokens)")
                generated_count += 1
                verb_example_count += 1
                
                # Update logger with token usage, duration, and verb info
                pipeline_logger.update_stats(prompt_tokens, completion_tokens, verb.english,
                                             file_duration, generated=True)
                
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
            # Write verb summary to log
            pipeline_logger.write_verb_summary(current_verb, verb_example_count,
                                               verb_prompt_tokens, verb_completion_tokens)
        
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
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user (Ctrl+C)")
        pipeline_logger.mark_interrupted()
        print(f"Generated {generated_count} examples before interruption.")
        total_tokens = total_prompt_tokens + total_completion_tokens
        print(f"\n📊 Token Usage (until interruption):")
        print(f"   Input tokens:  {total_prompt_tokens:,}")
        print(f"   Output tokens: {total_completion_tokens:,}")
        print(f"   Total tokens:  {total_tokens:,}")
        print(f"\n📝 Log file: {pipeline_logger.log_file}")
    except Exception as e:
        print(f"\n❌ PIPELINE FAILED due to error: {e}")
        pipeline_logger.set_error(e)
        print(f"Generated {generated_count} examples before failure.")
        total_tokens = total_prompt_tokens + total_completion_tokens
        print(f"\n📊 Token Usage (until failure):")
        print(f"   Input tokens:  {total_prompt_tokens:,}")
        print(f"   Output tokens: {total_completion_tokens:,}")
        print(f"   Total tokens:  {total_tokens:,}")
        print(f"\n📝 Log file: {pipeline_logger.log_file}")
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
        help='LLM provider to use: "gemini" (AI Studio) or "azure" (default: uses config.toml setting)'
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip generating files that already exist"
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
            provider=args.provider,
            skip_existing=args.skip_existing
        )
    else:
        top_n = args.top_n_verbs if args.top_n_verbs else 10
        main(
            language_level=args.language_level,
            top_n_verbs=top_n,
            tenses=args.tenses,
            pronouns=args.pronouns,
            polarities=args.polarities,
            provider=args.provider,
            skip_existing=args.skip_existing
        )

import csv
import json
import os
import re
import time
import atexit
import signal
import sys
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Optional, Any, Dict

import toml
from dotenv import load_dotenv
from grammer_metadata import (
    VerbTense, PersonalPronoun, LanguageLevel, TrainingExample,
    BatchTrainingExamples, VERB_FORM_INFOS, VerbPolarity
)

# Load environment variables
load_dotenv()

# Global state for Claude model rotation
CLAUDE_MODEL_INDEX = 0
CLAUDE_ROTATION_ENABLED = True


# LLM Call Logger
class LLMCallLogger:
    """Logger for individual LLM API calls"""
    def __init__(self):
        self.log_file = None
        self.csv_writer = None
        self.csv_file_handle = None
    
    def initialize(self, log_dir: Path):
        """Initialize CSV logger for LLM calls"""
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"llm_calls_{timestamp}.csv"
        
        # Open CSV file and write header
        self.csv_file_handle = open(self.log_file, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file_handle)
        self.csv_writer.writerow([
            'timestamp',
            'model_name',
            'prompt_tokens',
            'completion_tokens',
            'total_tokens',
            'duration_seconds',
            'error'
        ])
        self.csv_file_handle.flush()
        
        # Register cleanup handler
        atexit.register(self.close)
    
    def log_call(self, model_name: str, prompt_tokens: int, completion_tokens: int,
                 duration: float, error: Optional[str] = None):
        """Log an LLM API call
        
        Args:
            model_name: Name of the model used
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            duration: Duration of the call in seconds
            error: Error message if the call failed
        """
        if self.csv_writer is None:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_tokens = prompt_tokens + completion_tokens
        
        self.csv_writer.writerow([
            timestamp,
            model_name,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            f"{duration:.2f}",
            error or ''
        ])
        self.csv_file_handle.flush()
    
    def close(self):
        """Close the CSV file"""
        if self.csv_file_handle:
            self.csv_file_handle.close()
            self.csv_file_handle = None
            self.csv_writer = None


# Global LLM call logger instance
llm_call_logger = LLMCallLogger()


def get_pronoun_requirements_for_tense(tense: VerbTense, polarity: VerbPolarity) -> str:
    """Generate pronoun requirements text based on verb form type.
    
    Args:
        tense: The verb tense
        polarity: The verb polarity
    
    Returns:
        Formatted text describing which pronouns to generate for this tense
    """
    # Find the verb form info for this tense+polarity
    verb_form = None
    for vf in VERB_FORM_INFOS:
        if vf.verb_tense == tense and vf.polarity == polarity:
            verb_form = vf
            break
    
    if not verb_form:
        # Default to all pronouns if not found
        return """
## Generation Requirements

You must generate examples for **ALL combinations** of:
- **Pronouns**: ben, sen, o, biz, siz, onlar (6 total)
- **Polarities**: positive, negative (2 total)
- **Total**: 12 examples (6 pronouns × 2 polarities)
"""
    
    # Determine pronouns based on type_of_personal_pronoun
    if verb_form.type_of_personal_pronoun is None:
        # No personal pronouns (participles, infinitives, etc.)
        return """
## Generation Requirements

This verb form does NOT use personal pronouns (it's a participle, infinitive, or impersonal form).

You must generate **2 examples**:
- **Polarity**: positive (1 example)
- **Polarity**: negative (1 example)
- **Total**: 2 examples

For each example, set "personal_pronoun" to null and "personal_affix" to null (or appropriate participial suffix if applicable).
"""
    
    elif verb_form.type_of_personal_pronoun == 3:
        # Type 3: Imperatives - only sen, siz, o, onlar (not ben, biz)
        return """
## Generation Requirements

This is an **imperative** form (emir_kipi). Imperatives are NOT used with first-person pronouns (ben, biz).

You must generate examples for:
- **Pronouns**: sen, o, siz, onlar (4 total - excludes ben and biz)
- **Polarities**: positive, negative (2 total)
- **Total**: 8 examples (4 pronouns × 2 polarities)

**Imperative pronouns:**
- **sen** (you singular - informal command)
- **o** (he/she/it - third person polite request)
- **siz** (you plural/formal - polite command)
- **onlar** (they - third person polite request)
"""
    
    else:
        # Type 1 or 2: All personal pronouns
        return """
## Generation Requirements

You must generate examples for **ALL combinations** of:
- **Pronouns**: ben, sen, o, biz, siz, onlar (6 total)
- **Polarities**: positive, negative (2 total)
- **Total**: 12 examples (6 pronouns × 2 polarities)
"""


def get_json_schema_for_prompt(batch_mode: bool = False) -> str:
    """Generate JSON schema from Pydantic model for inclusion in prompt.
    
    Args:
        batch_mode: If True, use BatchTrainingExamples schema; if False, use single TrainingExample
    
    Returns:
        Formatted JSON schema string with example to inject into system prompt
    """
    # Get the JSON schema from Pydantic model
    if batch_mode:
        schema = BatchTrainingExamples.model_json_schema()
        
        # Create example instances using Pydantic models
        from grammer_metadata import TurkishVerb
        
        example1 = TrainingExample(
            verb_rank=1,
            verb_english="be",
            verb_russian="быть",
            verb_infinitive="olmak",
            turkish_verb=TurkishVerb(
                verb_full="oluyorum",
                root="ol",
                tense_affix="uyor",
                verb_tense=VerbTense.ŞimdikiZaman,
                personal_pronoun=PersonalPronoun.Ben,
                personal_affix="um",
                polarity=VerbPolarity.Positive,
                negative_affix=None
            ),
            english_example_sentence="I am a happy student today",
            russian_example_sentence="Я счастливый студент сегодня",
            turkish_example_sentence="Ben bugün mutlu bir öğrenciyim"
        )
        
        example2 = TrainingExample(
            verb_rank=1,
            verb_english="be",
            verb_russian="быть",
            verb_infinitive="olmak",
            turkish_verb=TurkishVerb(
                verb_full="olmuyorum",
                root="ol",
                tense_affix="uyor",
                verb_tense=VerbTense.ŞimdikiZaman,
                personal_pronoun=PersonalPronoun.Ben,
                personal_affix="um",
                polarity=VerbPolarity.Negative,
                negative_affix="m"
            ),
            english_example_sentence="I am not ready for this exam",
            russian_example_sentence="Я не готов к этому экзамену",
            turkish_example_sentence="Ben bu sınav için hazır olmuyorum"
        )
        
        batch_example = BatchTrainingExamples(examples=[example1, example2])
        example_json = json.loads(batch_example.model_dump_json())
        
    else:
        schema = TrainingExample.model_json_schema()
        
        # Create example instance using Pydantic models
        from grammer_metadata import TurkishVerb
        
        example_instance = TrainingExample(
            verb_rank=1,
            verb_english="be",
            verb_russian="быть",
            verb_infinitive="olmak",
            turkish_verb=TurkishVerb(
                verb_full="oluyorum",
                root="ol",
                tense_affix="uyor",
                verb_tense=VerbTense.ŞimdikiZaman,
                personal_pronoun=PersonalPronoun.Ben,
                personal_affix="um",
                polarity=VerbPolarity.Positive,
                negative_affix=None
            ),
            english_example_sentence="I am a student",
            russian_example_sentence="Я студент",
            turkish_example_sentence="Ben öğrenciyim"
        )
        
        example_json = json.loads(example_instance.model_dump_json())
    
    # Create a formatted schema description for the prompt
    schema_description = f"""
## JSON Output Schema

You must respond with valid JSON matching this exact schema:

```json
{json.dumps(schema, indent=2, ensure_ascii=False)}
```

## Example Output

```json
{json.dumps(example_json, indent=2, ensure_ascii=False)}
```

**IMPORTANT**:
- Return ONLY valid JSON, no markdown formatting, no explanations
- All fields are required unless marked as Optional
- Use exact enum values for verb_tense, personal_pronoun, polarity
- Ensure verb_full matches the combination of root + tense_affix + personal_affix (and negative_affix if present)
"""
    
    return schema_description


def get_grammar_rules_for_tense(tense: VerbTense, language: str = "english") -> str:
    """Load grammar rules for specific tense from grammar_reference.json.
    
    Args:
        tense: The verb tense to get rules for
        language: Language for the rules ("english" or "russian")
    
    Returns:
        Formatted grammar rules string to inject into prompt
    """
    # Load grammar reference
    grammar_file = Path(__file__).parent.parent / "frontend" / "public" / "grammar" / "grammar_reference.json"
    
    try:
        with open(grammar_file, 'r', encoding='utf-8') as f:
            grammar_data = json.load(f)
    except Exception as e:
        print(f"⚠️  Warning: Could not load grammar reference: {e}")
        return ""
    
    # Get tense-specific data
    tense_key = tense.value
    if tense_key not in grammar_data:
        print(f"⚠️  Warning: No grammar rules found for tense '{tense_key}'")
        return ""
    
    tense_data = grammar_data[tense_key]
    lang_data = tense_data.get(language, {})
    
    if not lang_data:
        return ""
    
    # Format grammar rules
    rules_text = f"""
## Grammar Rules for {lang_data.get('name', tense_key)}

**Description:** {lang_data.get('description', '')}

**Usage:**
"""
    
    # Add usage cases
    for usage in lang_data.get('usage', []):
        rules_text += f"- {usage}\n"
    
    # Add formation rules
    formation = lang_data.get('formation', {})
    if formation:
        rules_text += "\n**Formation:**\n"
        rules_text += f"- Positive: {formation.get('positive', '')}\n"
        rules_text += f"- Negative: {formation.get('negative', '')}\n"
        if 'vowel_harmony_note' in formation:
            rules_text += f"- Vowel Harmony: {formation['vowel_harmony_note']}\n"
    
    # Add affix information
    affixes = lang_data.get('affixes', {})
    if affixes:
        rules_text += "\n**Affixes:**\n"
        
        # Tense markers
        if 'tense_markers' in affixes:
            rules_text += "\nTense Markers:\n"
            for marker in affixes['tense_markers']:
                rules_text += f"- {marker['affix']}: {marker.get('description', '')}\n"
        
        # Personal endings
        if 'personal_endings' in affixes:
            rules_text += "\nPersonal Endings:\n"
            for ending in affixes['personal_endings']:
                rules_text += f"- {ending['pronoun']}: {ending['ending']} (e.g., {ending.get('example', '')})\n"
        
        # Negative affix
        if 'negative_affix' in affixes:
            rules_text += f"\nNegative Affix: {affixes['negative_affix']}\n"
    
    # Add examples
    examples = lang_data.get('examples', [])
    if examples:
        rules_text += "\n**Examples:**\n"
        for ex in examples[:5]:  # Limit to 5 examples
            rules_text += f"- {ex['turkish']} → {ex['translation']} ({ex.get('type', 'positive')})\n"
    
    return rules_text


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
    
    def log_batch_start(self, batch_num: int, total_batches: int, verb_turkish: str, 
                        verb_english: str, tense: str, expected_count: int):
        """Log the start of a batch processing"""
        if self.log_file is None:
            return
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"Batch {batch_num}/{total_batches}: {verb_english} ({verb_turkish}) + {tense}\n")
                f.write(f"  Expected: {expected_count} examples\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not write batch start log: {e}")
    
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


def load_verb_tense_exclusions() -> Dict[str, List[str]]:
    """Load verb-tense exclusion rules from JSON file.
    
    Returns:
        Dictionary mapping verb_infinitive to list of excluded tense names
    """
    exclusion_file = Path(__file__).parent.parent / "data" / "verb_tense_exclusions.json"
    if not exclusion_file.exists():
        return {}
    
    try:
        with open(exclusion_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Build lookup dictionary: verb_infinitive -> [excluded_tenses]
        exclusions = {}
        for item in data.get("exclusions", []):
            verb_infinitive = item.get("verb_infinitive")
            excluded_tenses = item.get("excluded_tenses", [])
            if verb_infinitive and excluded_tenses:
                exclusions[verb_infinitive] = excluded_tenses
        
        return exclusions
    except Exception as e:
        print(f"⚠️  Warning: Failed to load verb_tense_exclusions.json: {e}")
        return {}


def generate_combinations(
    verbs: List[VerbData],
    language_level: LanguageLevel
) -> List[Tuple[VerbData, VerbTense, Optional[PersonalPronoun], VerbPolarity]]:
    """Generate combinations of verbs × tenses × pronouns × polarity for given level"""
    combinations = []

    # Load exclusion rules
    exclusions = load_verb_tense_exclusions()
    excluded_count = 0

    # Filter verb forms by language level
    valid_verb_forms = [
        vf for vf in VERB_FORM_INFOS
        if vf.language_level.value <= language_level.value
    ]
    
    for verb in verbs:
        # Get excluded tenses for this verb
        excluded_tenses = exclusions.get(verb.turkish, [])
        
        for verb_form in valid_verb_forms:
            # Skip if this verb+tense combination is excluded
            if verb_form.verb_tense.value in excluded_tenses:
                excluded_count += 1
                continue
            # Handle pronouns based on verb form requirements
            if verb_form.type_of_personal_pronoun is None:
                # No personal pronouns (e.g., participles, infinitives)
                combinations.append((verb, verb_form.verb_tense, None, verb_form.polarity))
            elif verb_form.type_of_personal_pronoun == 3:
                # Type 3: Imperatives - only sen, siz, o, onlar (not ben, biz)
                pronouns = [
                    PersonalPronoun.Sen,
                    PersonalPronoun.O_Third,
                    PersonalPronoun.Siz,
                    PersonalPronoun.Onlar
                ]
                for pronoun in pronouns:
                    combinations.append((verb, verb_form.verb_tense, pronoun, verb_form.polarity))
            else:
                # Type 1 or 2: Add all personal pronouns
                pronouns = [
                    PersonalPronoun.Ben, PersonalPronoun.Sen,
                    PersonalPronoun.O_Third, PersonalPronoun.Biz,
                    PersonalPronoun.Siz, PersonalPronoun.Onlar
                ]
                for pronoun in pronouns:
                    combinations.append((verb, verb_form.verb_tense, pronoun, verb_form.polarity))
    
    if excluded_count > 0:
        print(f"⏭️  Excluded {excluded_count} semantically redundant verb+tense combinations")
    
    return combinations


def load_prompt_template(batch_mode: bool = False) -> str:
    """Load the prompt template from the prompt file
    
    Args:
        batch_mode: If True, load batch prompt; otherwise load single-example prompt
    """
    if batch_mode:
        prompt_file = Path(__file__).parent.parent / "prompts" / "create_training_example_batch.prompt.md"
    else:
        prompt_file = Path(__file__).parent.parent / "prompts" / "create_training_example.prompt.md"
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


def clean_llm_response(response_text: str) -> str:
    """Clean LLM response by removing markdown code blocks and provider-specific tags.
    
    Args:
        response_text: Raw response text from LLM
    
    Returns:
        Cleaned response text with only the JSON content
    """
    response_text = response_text.strip()
    
    # Handle DeepSeek's <think> tags - extract content after </think>
    if '<think>' in response_text and '</think>' in response_text:
        think_end = response_text.find('</think>')
        response_text = response_text[think_end + 8:].strip()
    
    # Strip markdown code block markers
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    elif response_text.startswith('```'):
        response_text = response_text[3:]  # Remove ```
    
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove trailing ```
    
    return response_text.strip()


def validate_and_parse_response(
    response_text: str,
    batch_mode: bool = False
) -> tuple[TrainingExample | BatchTrainingExamples, str | None]:
    """Parse and validate LLM response against Pydantic schema.
    
    Args:
        response_text: Cleaned response text (JSON string)
        batch_mode: If True, validate against BatchTrainingExamples; otherwise TrainingExample
    
    Returns:
        Tuple of (parsed_model, error_message)
        - If successful: (model_instance, None)
        - If failed: (None, error_message_string)
    """
    # Parse JSON
    try:
        json_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON. Error: {e}\nResponse text: {response_text[:500]}"
    
    # Fix common null value issues in turkish_verb fields
    # Sometimes AI models return null for tense_affix in negative forms, fix it to empty string
    if batch_mode and "examples" in json_data:
        for example in json_data["examples"]:
            if "turkish_verb" in example and isinstance(example["turkish_verb"], dict):
                if example["turkish_verb"].get("tense_affix") is None:
                    example["turkish_verb"]["tense_affix"] = ""
    elif "turkish_verb" in json_data and isinstance(json_data["turkish_verb"], dict):
        if json_data["turkish_verb"].get("tense_affix") is None:
            json_data["turkish_verb"]["tense_affix"] = ""
    
    # Validate against Pydantic model
    try:
        if batch_mode:
            model_instance = BatchTrainingExamples(**json_data)
        else:
            model_instance = TrainingExample(**json_data)
        
        return model_instance, None
    except Exception as validation_error:
        error_msg = (
            f"Failed to validate JSON against {'BatchTrainingExamples' if batch_mode else 'TrainingExample'} schema.\n"
            f"Error: {validation_error}\n"
            f"JSON data: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}"
        )
        return None, error_msg


def validate_batch_completeness(
    batch: BatchTrainingExamples,
    tense: VerbTense,
    expected_polarities: list[VerbPolarity]
) -> tuple[bool, str | None]:
    """Validate that batch contains all required pronoun+polarity combinations.
    
    Args:
        batch: BatchTrainingExamples instance to validate
        tense: The verb tense being generated
        expected_polarities: List of polarities that should be present
    
    Returns:
        Tuple of (is_complete, error_message)
        - If complete: (True, None)
        - If incomplete: (False, error_message_string describing what's missing)
    """
    # Find the verb form info for this tense
    verb_form = None
    for vf in VERB_FORM_INFOS:
        if vf.verb_tense == tense:
            verb_form = vf
            break
    
    if not verb_form:
        # Can't validate without verb form info, assume valid
        return True, None
    
    # Determine expected pronouns based on type_of_personal_pronoun
    if verb_form.type_of_personal_pronoun is None:
        # Participles/impersonal forms - expect 2 examples (positive, negative)
        expected_count = len(expected_polarities)
        if len(batch.examples) != expected_count:
            return False, (
                f"Expected {expected_count} examples (1 per polarity for impersonal form), "
                f"but got {len(batch.examples)}"
            )
    elif verb_form.type_of_personal_pronoun == 3:
        # Imperatives - expect 4 pronouns × polarities
        expected_pronouns = [
            PersonalPronoun.Sen,
            PersonalPronoun.O_Third,
            PersonalPronoun.Siz,
            PersonalPronoun.Onlar
        ]
        expected_count = len(expected_pronouns) * len(expected_polarities)
        
        if len(batch.examples) != expected_count:
            return False, (
                f"Expected {expected_count} examples "
                f"({len(expected_pronouns)} pronouns × {len(expected_polarities)} polarities), "
                f"but got {len(batch.examples)}"
            )
        
        # Check that all combinations are present
        missing = []
        for pronoun in expected_pronouns:
            for polarity in expected_polarities:
                found = any(
                    ex.turkish_verb.personal_pronoun == pronoun and
                    ex.turkish_verb.polarity == polarity
                    for ex in batch.examples
                )
                if not found:
                    missing.append(f"{pronoun.value}/{polarity.value}")
        
        if missing:
            return False, f"Missing pronoun/polarity combinations: {', '.join(missing)}"
    
    else:
        # Type 1 or 2: All pronouns - expect 6 pronouns × polarities
        expected_pronouns = [
            PersonalPronoun.Ben, PersonalPronoun.Sen,
            PersonalPronoun.O_Third, PersonalPronoun.Biz,
            PersonalPronoun.Siz, PersonalPronoun.Onlar
        ]
        expected_count = len(expected_pronouns) * len(expected_polarities)
        
        if len(batch.examples) != expected_count:
            return False, (
                f"Expected {expected_count} examples "
                f"({len(expected_pronouns)} pronouns × {len(expected_polarities)} polarities), "
                f"but got {len(batch.examples)}"
            )
        
        # Check that all combinations are present
        missing = []
        for pronoun in expected_pronouns:
            for polarity in expected_polarities:
                found = any(
                    ex.turkish_verb.personal_pronoun == pronoun and
                    ex.turkish_verb.polarity == polarity
                    for ex in batch.examples
                )
                if not found:
                    missing.append(f"{pronoun.value}/{polarity.value}")
        
        if missing:
            return False, f"Missing pronoun/polarity combinations: {', '.join(missing)}"
    
    return True, None


def call_dial_api(
    prompt_text: str,
    config: dict,
    provider: str,
    conversation_history: list[dict] = None,
    claude_model_index: int = 0,
    timeout_retries: int = 1
) -> tuple[str, int, int, str]:
    """Make a request to DIAL API and return the response.
    
    Args:
        prompt_text: The prompt to send (for first message) or None if using conversation_history
        config: Configuration dictionary
        provider: Provider name (openai, claude, gemini, deepseek)
        conversation_history: Optional conversation history for retry logic
        claude_model_index: Index in CLAUDE_MODEL_ROTATION list (for rotation)
        timeout_retries: Number of times to retry on timeout errors (default: 1)
    
    Returns:
        Tuple of (response_text, prompt_tokens, completion_tokens, model_name)
    
    Raises:
        ValueError: If API request fails or configuration is invalid
    """
    # Get DIAL API configuration
    api_key = os.getenv('DIAL_API_KEY')
    if not api_key:
        raise ValueError("Please set DIAL_API_KEY in your environment variables")
    
    # Get model ID based on provider
    dial_config = config.get('DIAL_API', {})
    
    # For Claude, use rotation list if available
    if provider == 'claude':
        rotation_list = dial_config.get('CLAUDE_MODEL_ROTATION', [])
        if rotation_list and claude_model_index < len(rotation_list):
            model_id = rotation_list[claude_model_index]
        else:
            model_id = dial_config.get('CLOUD_MODEL_NAME', 'anthropic.claude-haiku-4-5-20251001-v1:0')
    else:
        provider_model_map = {
            'openai': dial_config.get('OPENAI_MODEL_NAME', 'gpt-4o-mini-2024-07-18'),
            'gemini': dial_config.get('GEMINI_MODEL_NAME', 'gemini-2.5-flash'),
            'deepseek': dial_config.get('DEEP_SEEK_MODEL_NAME', 'deepseek-r1'),
            'llama': dial_config.get('LLAMA_MODEL_NAME', 'meta.llama4-scout-17b-instruct-v1:0')
        }
        model_id = provider_model_map.get(provider, provider_model_map.get('openai'))
    
    model_name = f"{provider.upper()} - {model_id}"
    
    # Build DIAL API URL
    api_url_template = dial_config.get('DIAL_API_ENDPOINT')
    if not api_url_template:
        raise ValueError("DIAL_API_ENDPOINT not found in config.toml")
    api_url = api_url_template.format(model_id=model_id)
    
    # Prepare messages
    if conversation_history:
        messages = conversation_history
    else:
        messages = [{"role": "user", "content": prompt_text}]
    
    # Prepare DIAL API request
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Use max_completion_tokens for OpenAI models, max_tokens for others
    max_tokens_key = "max_completion_tokens" if provider == "openai" else "max_tokens"
    
    payload = {
        "messages": messages,
        max_tokens_key: config['generation'].get('max_output_tokens', 8192),
        "stream": False
    }
    
    # OpenAI gpt-5-nano only supports temperature=1 (default), others support custom temperature
    if provider != "openai":
        payload["temperature"] = config['generation']['temperature']
    
    # Track start time
    start_time = time.time()
    error_msg = None
    prompt_tokens = 0
    completion_tokens = 0
    
    # Retry loop for timeout and 502 errors
    for attempt in range(timeout_retries + 1):
        try:
            # Make API request
            response = requests.post(api_url, headers=headers, json=payload, timeout=300)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Check for 502 errors (retryable)
            if response.status_code == 502:
                if attempt < timeout_retries:
                    wait_time = 10 * (attempt + 1)  # 10s, 20s, 30s...
                    print(f"   ⚠️  502 error: {response.text} (attempt {attempt + 1}/{timeout_retries + 1})")
                    print(f"   🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    start_time = time.time()  # Reset timer for retry
                    continue
                else:
                    # Final 502 - log and raise
                    error_msg = f"502 error after {timeout_retries + 1} attempts: {response.text}"
                    llm_call_logger.log_call(model_name, 0, 0, duration, error_msg)
                    raise ValueError(
                        f"DIAL API request failed after {timeout_retries + 1} attempts. "
                        f"Status: 502, Response: {response.text}"
                    )
            
            # Check for other non-200 responses (not retryable)
            if response.status_code != 200:
                error_msg = f"Status {response.status_code}: {response.text}"
                llm_call_logger.log_call(model_name, 0, 0, duration, error_msg)
                raise ValueError(
                    f"DIAL API request failed. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
            
            data = response.json()
            break  # Success, exit retry loop
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as timeout_error:
            duration = time.time() - start_time
            timeout_type = type(timeout_error).__name__
            if attempt < timeout_retries:
                wait_time = 10 * (attempt + 1)  # 10s, 20s, 30s...
                print(f"   ⚠️  {timeout_type} after {duration:.1f}s (attempt {attempt + 1}/{timeout_retries + 1})")
                print(f"   🔄 Retrying in {wait_time}s...")
                time.sleep(wait_time)
                start_time = time.time()  # Reset timer for retry
                continue
            else:
                # Final timeout - log and raise
                error_msg = f"{timeout_type} after {duration:.1f}s (all {timeout_retries + 1} attempts failed)"
                llm_call_logger.log_call(model_name, 0, 0, duration, error_msg)
                raise
    
    # Process successful response
    try:
        # Calculate final duration
        duration = time.time() - start_time
        
        # Extract response content
        if 'choices' not in data or len(data['choices']) == 0:
            error_msg = "No choices in DIAL API response"
            llm_call_logger.log_call(model_name, 0, 0, duration, error_msg)
            raise ValueError("No choices in DIAL API response")
        
        response_text = data['choices'][0]['message']['content']
        
        # Post-process DeepSeek R1 responses to remove reasoning tags
        if 'deepseek' in model_name.lower() and 'r1' in model_name.lower():
            import re
            # Remove <think>...</think> tags and their content
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
            # Clean up extra whitespace
            response_text = response_text.strip()
        
        # Extract token usage
        usage = data.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        
        # FAIL if we don't have accurate token counts
        if prompt_tokens == 0 or completion_tokens == 0:
            error_msg = f"No token usage: prompt={prompt_tokens}, completion={completion_tokens}"
            llm_call_logger.log_call(model_name, prompt_tokens, completion_tokens, duration, error_msg)
            raise ValueError(
                f"Failed to get token usage from DIAL API response. "
                f"Got prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}."
            )
        
        # Log successful call
        llm_call_logger.log_call(model_name, prompt_tokens, completion_tokens, duration)
        
        return response_text, prompt_tokens, completion_tokens, model_name
    
    except Exception as e:
        # Log failed call if we haven't already
        duration = time.time() - start_time
        if error_msg is None:
            error_msg = str(e)
            llm_call_logger.log_call(model_name, prompt_tokens, completion_tokens, duration, error_msg)
        raise


def validate_verb_root_in_sentence(
    verb_root: str,
    turkish_sentence: str,
    verb_full: str
) -> Tuple[bool, str]:
    """
    Validate that the verb root appears in the Turkish sentence.
    Accounts for Turkish consonant softening: p→b, ç→c, t→d, k→ğ
    
    Args:
        verb_root: The root of the verb (e.g., "yap", "git")
        turkish_sentence: The Turkish example sentence
        verb_full: The complete conjugated verb form
        
    Returns:
        (is_valid, error_message) - error_message is empty if valid
    """
    # First check if full verb appears in sentence
    if verb_full.lower() in turkish_sentence.lower():
        return True, ""
    
    # Check if root appears directly
    if verb_root.lower() in turkish_sentence.lower():
        return True, ""
    
    # Check for consonant softening variations
    # Turkish consonant softening rules: p→b, ç→c, t→d, k→ğ (when between vowels)
    softening_map = {
        'p': 'b',
        'ç': 'c',
        't': 'd',
        'k': 'ğ'
    }
    
    # Try each possible softening of the last consonant
    for i, char in enumerate(verb_root):
        if char in softening_map:
            softened_root = verb_root[:i] + softening_map[char] + verb_root[i+1:]
            if softened_root.lower() in turkish_sentence.lower():
                return True, ""
    
    # Root not found in any form
    return False, (
        f"Verb root '{verb_root}' not found in sentence: '{turkish_sentence}'. "
        f"The sentence may be using a different verb. Please use the correct verb '{verb_root}' or its softened form."
    )


def generate_training_example(
    verb: VerbData,
    tense: VerbTense,
    pronoun: Optional[PersonalPronoun] = None,
    polarity: Optional[VerbPolarity] = None,
    language_level: LanguageLevel = LanguageLevel.A1,
    config: Optional[dict] = None,
    provider: str = "openai",
    rate_limiter: Optional[RateLimiter] = None,
    max_retries: int = 3,
    timeout_retries: int = 1
) -> Tuple[List[TrainingExample], int, int]:
    """Generate training examples using DIAL API.
    
    This function works in two modes:
    1. **Single mode**: If pronoun AND polarity are specified, generates one example
    2. **Batch mode**: If pronoun OR polarity is None, generates all pronoun×polarity combinations
    
    Args:
        verb: Verb data from CSV
        tense: Verb tense to use
        pronoun: Personal pronoun (None = batch mode for all pronouns)
        polarity: Verb polarity (None = batch mode for all polarities)
        language_level: Language level for examples
        config: Configuration dictionary (will be loaded if None)
        provider: LLM provider to use (openai, claude, gemini, deepseek)
        rate_limiter: Optional rate limiter to control request frequency
        max_retries: Maximum number of retries on validation errors
        timeout_retries: Number of times to retry on timeout errors (default: 1)
        max_retries: Maximum number of retries on validation errors
    
    Returns:
        Tuple of (List[TrainingExample], prompt_tokens, completion_tokens)
        - Single mode: Returns list with 1 example
        - Batch mode: Returns list with multiple examples (2-12 depending on verb form)
    """
    def extract_retry_delay(error_message: str) -> int:
        """Extract retry delay in seconds from error message"""
        match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', str(error_message))
        if match:
            return int(match.group(1))
        return 60
    
    # Load config if not provided
    if config is None:
        config = load_config()
        if not config:
            raise ValueError("Failed to load configuration")
    
    # Determine mode: batch if pronoun OR polarity is None
    batch_mode = (pronoun is None or polarity is None)
    
    # Determine expected polarities for batch mode
    if batch_mode:
        expected_polarities = [VerbPolarity.Positive, VerbPolarity.Negative]
    else:
        expected_polarities = [polarity]
    
    # Load appropriate prompt template
    prompt_template_str = load_prompt_template(batch_mode=batch_mode)
    
    # Build prompt from template
    json_schema = get_json_schema_for_prompt(batch_mode=batch_mode)
    grammar_rules = get_grammar_rules_for_tense(tense, language="english")
    
    if batch_mode:
        # Batch mode: get pronoun requirements dynamically
        pronoun_requirements = get_pronoun_requirements_for_tense(tense, VerbPolarity.Positive)
        
        prompt_text = prompt_template_str.format(
            json_schema=json_schema,
            grammar_rules=grammar_rules,
            pronoun_requirements=pronoun_requirements,
            verb_english=verb.english,
            verb_infinitive=verb.turkish,
            verb_tense=tense.value,
            language_level=language_level.value
        )
    else:
        # Single mode: specify pronoun and polarity
        prompt_text = prompt_template_str.format(
            json_schema=json_schema,
            grammar_rules=grammar_rules,
            verb_english=verb.english,
            verb_infinitive=verb.turkish,
            verb_tense=tense.value,
            personal_pronoun=pronoun.value,
            language_level=language_level.value,
            polarity=polarity.value
        )
    
    conversation_history = None
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    # Retry loop for validation errors
    for attempt in range(max_retries + 1):
        try:
            # Apply rate limiting
            if rate_limiter:
                rate_limiter.wait_if_needed()
            
            # Call DIAL API (with Claude model rotation support)
            try:
                global CLAUDE_MODEL_INDEX, CLAUDE_ROTATION_ENABLED
                
                response_text, prompt_tokens, completion_tokens, model_name = call_dial_api(
                    prompt_text if conversation_history is None else None,
                    config,
                    provider,
                    conversation_history,
                    claude_model_index=CLAUDE_MODEL_INDEX if provider == 'claude' else 0,
                    timeout_retries=timeout_retries
                )
                
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
                
            except (requests.exceptions.RequestException, ValueError) as req_error:
                # Handle rate limit errors
                error_str = str(req_error)
                is_rate_limit = '429' in error_str or 'rate limit' in error_str.lower()
                
                # Check for daily/quota limits (NOT retryable)
                is_quota_exceeded = any(phrase in error_str.lower() for phrase in [
                    'day limit', 'daily limit', 'daily token limit', 
                    'quota exceeded', 'exceeded your daily'
                ])
                
                if is_quota_exceeded:
                    print(f"   ❌ DAILY QUOTA EXCEEDED - Cannot retry")
                    print(f"   📊 Error: {error_str[:200]}")
                    raise ValueError(
                        "Daily token quota exceeded. Wait until tomorrow or switch to a different provider."
                    )
                
                if is_rate_limit:
                    # Check if we're using Claude and rotation is enabled
                    if provider == 'claude' and CLAUDE_ROTATION_ENABLED:
                        rotation_list = config.get('DIAL_API', {}).get('CLAUDE_MODEL_ROTATION', [])
                        if rotation_list and CLAUDE_MODEL_INDEX < len(rotation_list) - 1:
                            # Try next model in rotation
                            CLAUDE_MODEL_INDEX += 1
                            next_model = rotation_list[CLAUDE_MODEL_INDEX]
                            print(f"   🔄 Daily limit hit! Rotating to next Claude model: {next_model}")
                            print(f"      Model {CLAUDE_MODEL_INDEX + 1}/{len(rotation_list)} in rotation")
                            # Retry immediately with new model (don't count as retry attempt)
                            continue
                        elif rotation_list and CLAUDE_MODEL_INDEX >= len(rotation_list) - 1:
                            print(f"   ❌ All {len(rotation_list)} Claude models exhausted their daily limits!")
                            raise ValueError(
                                "All Claude models have hit their daily token limits. "
                                "Try again tomorrow or use a different provider."
                            )
                    
                    # Not Claude or no rotation available - use normal retry logic
                    if attempt < max_retries:
                        retry_delay = extract_retry_delay(error_str)
                        print(f"   ⚠️  Rate limit hit (attempt {attempt + 1}/{max_retries + 1})")
                        if rate_limiter:
                            rate_limiter.handle_rate_limit_error(retry_delay)
                        else:
                            print(f"   ⏳ Waiting {retry_delay}s before retry...")
                            time.sleep(retry_delay)
                        continue
                
                # Re-raise other network errors
                raise req_error
            
            # Clean LLM response
            cleaned_response = clean_llm_response(response_text)
            
            # Validate and parse
            result, error_msg = validate_and_parse_response(cleaned_response, batch_mode=batch_mode)
            
            if result is None:
                # Validation failed
                if attempt < max_retries:
                    print(f"   ⚠️  Validation failed (attempt {attempt + 1}/{max_retries + 1}): {error_msg[:100]}")
                    
                    # Build conversation history for retry with error feedback
                    if conversation_history is None:
                        conversation_history = [
                            {"role": "user", "content": prompt_text},
                            {"role": "assistant", "content": response_text}
                        ]
                    else:
                        conversation_history.append({"role": "assistant", "content": response_text})
                    
                    # Add error feedback
                    feedback_message = (
                        f"The previous response failed validation:\n\n{error_msg}\n\n"
                        f"Please fix the issues and provide a corrected JSON response."
                    )
                    conversation_history.append({"role": "user", "content": feedback_message})
                    
                    continue
                else:
                    # Max retries reached
                    print(f"   ❌ Max retries ({max_retries}) reached for validation")
                    raise ValueError(f"Validation failed after {max_retries} retries: {error_msg}")
            
            # Post-validation: Check verb root in sentence(s)
            verb_root_errors = []
            examples_to_check = result.examples if batch_mode else [result]
            
            for example in examples_to_check:
                is_valid, root_error = validate_verb_root_in_sentence(
                    example.turkish_verb.root,
                    example.turkish_example_sentence,
                    example.turkish_verb.verb_full
                )
                if not is_valid:
                    verb_root_errors.append(root_error)
            
            if verb_root_errors:
                # Verb root validation failed
                if attempt < max_retries:
                    error_summary = "\n".join(f"- {err}" for err in verb_root_errors)
                    print(f"   ⚠️  Verb root mismatch (attempt {attempt + 1}/{max_retries + 1})")
                    
                    # Build conversation history for retry with error feedback
                    if conversation_history is None:
                        conversation_history = [
                            {"role": "user", "content": prompt_text},
                            {"role": "assistant", "content": response_text}
                        ]
                    else:
                        conversation_history.append({"role": "assistant", "content": response_text})
                    
                    # Add verb root error feedback
                    feedback_message = (
                        f"CRITICAL ERROR: The verb root does not match the sentence:\n\n"
                        f"{error_summary}\n\n"
                        f"You MUST use the verb '{verb.turkish}' "
                        f"(root: '{examples_to_check[0].turkish_verb.root}') in the Turkish sentence. "
                        f"Do NOT use different verbs. Remember that the root may undergo consonant softening "
                        f"(p→b, ç→c, t→d, k→ğ) but it must be recognizable as the same verb.\n\n"
                        f"Please provide a corrected JSON response with the correct verb."
                    )
                    conversation_history.append({"role": "user", "content": feedback_message})
                    
                    continue
                else:
                    # Max retries reached
                    print(f"   ❌ Max retries ({max_retries}) reached for verb root validation")
                    error_summary = "\n".join(verb_root_errors)
                    raise ValueError(f"Verb root mismatch after {max_retries} retries:\n{error_summary}")
            
            # Handle batch mode: validate completeness
            if batch_mode:
                is_complete, completeness_error = validate_batch_completeness(
                    result,
                    tense,
                    expected_polarities
                )
                
                if not is_complete:
                    # Batch incomplete
                    if attempt < max_retries:
                        print(f"   ⚠️  Batch incomplete (attempt {attempt + 1}/{max_retries + 1}): {completeness_error}")
                        
                        # Build conversation history for retry with error feedback
                        if conversation_history is None:
                            conversation_history = [
                                {"role": "user", "content": prompt_text},
                                {"role": "assistant", "content": response_text}
                            ]
                        else:
                            conversation_history.append({"role": "assistant", "content": response_text})
                        
                        # Add completeness feedback
                        feedback_message = (
                            f"The batch is incomplete:\n\n{completeness_error}\n\n"
                            f"Please provide ALL required examples in your corrected JSON response."
                        )
                        conversation_history.append({"role": "user", "content": feedback_message})
                        
                        continue
                    else:
                        # Max retries reached
                        print(f"   ❌ Max retries ({max_retries}) reached for completeness check")
                        raise ValueError(
                            f"Batch incomplete after {max_retries} retries for verb '{verb.turkish}' ({verb.english}) "
                            f"+ tense '{tense.value}': {completeness_error}"
                        )
                
                # Success! Override verb_rank, verb_russian, and add metadata in all examples
                generation_timestamp = datetime.now(timezone.utc).isoformat()
                
                for example in result.examples:
                    example.verb_rank = verb.rank
                    example.verb_russian = verb.russian
                    example.generated_by_model = model_name
                    example.generated_at = generation_timestamp
                
                return result.examples, total_prompt_tokens, total_completion_tokens
            else:
                # Single mode: return list with one example
                generation_timestamp = datetime.now(timezone.utc).isoformat()
                
                result.verb_rank = verb.rank
                result.verb_russian = verb.russian
                result.generated_by_model = model_name
                result.generated_at = generation_timestamp
                
                return [result], total_prompt_tokens, total_completion_tokens
            
        except Exception as outer_error:
            # Handle fatal errors
            error_str = str(outer_error)
            
            # Check for daily quota limit (more comprehensive patterns)
            is_daily_quota_exceeded = any(phrase in error_str.lower() for phrase in [
                'day limit', 'daily limit', 'daily token limit',
                'quota exceeded', 'exceeded your daily',
                'generate_requests_per_day', 'generaterequestsperday'
            ])
            
            if is_daily_quota_exceeded:
                print("   ❌ FATAL: Daily quota limit reached!")
                print(f"   📊 Error: {error_str[:300]}")
                raise RuntimeError("Daily quota limit reached. Cannot continue.") from outer_error
            
            # Check for per-minute rate limit (retryable)
            if '429' in error_str or 'RateLimitReached' in error_str or 'rate limit' in error_str.lower():
                if attempt < max_retries:
                    retry_delay = extract_retry_delay(error_str)
                    print(f"   ⚠️  Rate limit hit during setup (attempt {attempt + 1}/{max_retries + 1})")
                    if rate_limiter:
                        rate_limiter.handle_rate_limit_error(retry_delay)
                    else:
                        print(f"   ⏳ Waiting {retry_delay}s before retry...")
                        time.sleep(retry_delay)
                    continue
            
            # Fatal error - stop the pipeline
            if isinstance(outer_error, RuntimeError) and 'Daily quota limit' in str(outer_error):
                raise outer_error
            
            mode_desc = "batch" if batch_mode else f"example ({pronoun.value}, {polarity.value})"
            print(f"\n❌ FATAL ERROR generating {mode_desc} for {verb.english} ({tense.value})")
            print(f"Error details: {outer_error}")
            raise outer_error
    
    # Should never reach here
    return [], 0, 0


def save_training_example(example: TrainingExample, output_dir: Path, polarity: VerbPolarity,
                          verb: Optional['VerbData'] = None) -> Path:
    """Save training example as JSON file with proper naming convention

    Args:
        example: The training example to save
        output_dir: Base output directory
        polarity: Verb polarity (positive/negative)
        verb: Optional VerbData to ensure consistent folder naming with CSV

    Returns:
        Path: The path to the saved file
        
    Raises:
        ValueError: If the example fails validation
    """
    # Validate the example before saving
    is_valid, errors = example.validate()
    if not is_valid:
        error_msg = f"Training example validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
        error_msg += f"\n\nExample data:\n"
        error_msg += f"  Pronoun: {example.turkish_verb.personal_pronoun}\n"
        error_msg += f"  Verb full: {example.turkish_verb.verb_full}\n"
        error_msg += f"  Personal affix: {example.turkish_verb.personal_affix}\n"
        error_msg += f"  Turkish sentence: {example.turkish_example_sentence}\n"
        raise ValueError(error_msg)
    
    # Create folder structure: verb_english/ (without "to " prefix at the beginning)
    # Use verb.english if provided (from CSV) for consistency, otherwise fall back to example
    verb_name = verb.english if verb else example.verb_english
    if verb_name.startswith("to "):
        verb_name = verb_name[3:]  # Remove "to " from the beginning
    verb_name = verb_name.replace(" ", "_")
    verb_folder = output_dir / verb_name
    verb_folder.mkdir(parents=True, exist_ok=True)    # Create filename: pronoun_infinitive_tense_polarity.json
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
    start_from: int = 1,
    specific_verbs: Optional[List[str]] = None,
    tenses: Optional[List[str]] = None,
    pronouns: Optional[List[str]] = None,
    polarities: Optional[List[str]] = None,
    provider: Optional[str] = None,
    skip_existing: bool = False,
    timeout_retries: int = 1
):
    """Main pipeline function
    
    Args:
        language_level: Target language level (A1, A2, B1, B2)
        top_n_verbs: Number of top verbs to process from the list
        start_from: Position in the verb list to start from (1-indexed, default: 1)
        specific_verbs: List of specific verb names (English) to process
        tenses: List of specific tenses to generate (None = all). Values: şimdiki_zaman, geçmiş_zaman, geniş_zaman
        pronouns: List of specific pronouns to generate (None = all). Values: ben, sen, o, biz, siz, onlar
        polarities: List of specific polarities to generate (None = all). Values: positive, negative
        provider: LLM provider to use ("gemini" or "azure"). If None, uses default from config
        skip_existing: If True, skip combinations that already have generated files
        timeout_retries: Number of times to retry on timeout errors (default: 1)
    """
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration. Exiting.")
        return
    
    # Determine provider
    if provider is None:
        provider = config.get('DIAL_API', {}).get('DEFAULT_PROVIDER', 'openai')
    
    # Ensure provider is valid (DIAL API supports multiple providers)
    valid_providers = ['openai', 'claude', 'gemini', 'deepseek', 'llama']
    assert provider in valid_providers, f"Invalid provider: {provider}. Must be one of {valid_providers}"
    
    # Get model name for logging
    dial_config = config.get('DIAL_API', {})
    
    # For Claude, show the active model from rotation
    if provider == 'claude':
        rotation_list = dial_config.get('CLAUDE_MODEL_ROTATION', [])
        if rotation_list:
            active_model = rotation_list[CLAUDE_MODEL_INDEX]
            model_name = f"{provider.upper()} - {active_model} (model {CLAUDE_MODEL_INDEX + 1}/{len(rotation_list)})"
        else:
            active_model = dial_config.get('CLOUD_MODEL_NAME', 'anthropic.claude-haiku-4-5-20251001-v1:0')
            model_name = f"{provider.upper()} - {active_model}"
    else:
        provider_model_map = {
            'openai': dial_config.get('OPENAI_MODEL_NAME', 'gpt-4o-mini-2024-07-18'),
            'gemini': dial_config.get('GEMINI_MODEL_NAME', 'gemini-2.5-flash'),
            'deepseek': dial_config.get('DEEP_SEEK_MODEL_NAME', 'deepseek-r1'),
            'llama': dial_config.get('LLAMA_MODEL_NAME', 'meta.llama4-scout-17b-instruct-v1:0')
        }
        model_name = f"{provider.upper()} - {provider_model_map.get(provider, 'unknown')}"
    
    # Initialize logger
    project_root = Path(__file__).parent.parent
    log_dir = project_root / "logs"
    
    logger_args = {
        "language_level": language_level,
        "top_n_verbs": top_n_verbs,
        "start_from": start_from,
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
    
    # Initialize LLM call logger
    llm_call_logger.initialize(log_dir)
    print(f"📝 LLM calls logging to: {llm_call_logger.log_file}")
    
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
        if start_from > 1:
            end_position = start_from + top_n_verbs - 1
            print(f"Processing verbs {start_from} to {end_position} (top {top_n_verbs} from position {start_from})")
        else:
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
        # Validate start_from parameter
        if start_from < 1:
            print("⚠️  Warning: start_from must be >= 1, using 1 instead")
            start_from = 1
        
        if start_from > len(all_verbs):
            print(f"❌ Error: start_from ({start_from}) exceeds total verbs ({len(all_verbs)})")
            return
        
        # Calculate slice indices (convert from 1-indexed to 0-indexed)
        start_idx = start_from - 1
        end_idx = start_idx + top_n_verbs
        
        # Limit to top N verbs starting from position M
        verbs = all_verbs[start_idx:end_idx]
        actual_count = len(verbs)
        
        if actual_count < top_n_verbs:
            print(f"⚠️  Warning: Only {actual_count} verbs available from position {start_from}")
        
        print(f"Loaded {len(all_verbs)} verbs, processing {actual_count} verbs (positions {start_from} to {start_from + actual_count - 1})")
    
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
        if pronouns and (pronoun is None or pronoun.value not in pronouns):
            continue
        # Filter by polarity
        if polarities and polarity.value not in polarities:
            continue
        filtered_combinations.append((verb, tense, pronoun, polarity))
    
    combinations = filtered_combinations
    print(f"Generated {len(combinations)} combinations (after filtering)")
    
    # Determine generation mode based on filters
    use_batch_mode = (pronouns is None and polarities is None)
    
    if use_batch_mode:
        print("🚀 Using BATCH mode (generating all pronoun×polarity combinations per verb+tense)")
        
        # Group combinations by verb+tense for batch processing
        from collections import defaultdict
        verb_tense_groups = defaultdict(list)
        for verb, tense, pronoun, polarity in combinations:
            verb_tense_groups[(verb, tense)].append((pronoun, polarity))
        
        print(f"   → {len(verb_tense_groups)} unique verb+tense combinations")
    else:
        print("📝 Using SINGLE mode (generating individual examples)")
    
    # Generate training examples
    print("Generating training examples...")
    generated_count = 0
    skipped_count = 0
    skipped_existing_count = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    # Track per-verb statistics
    current_verb = None
    verb_prompt_tokens = 0
    verb_completion_tokens = 0
    verb_example_count = 0
    
    try:
        if use_batch_mode:
            # BATCH MODE: Process by verb+tense groups
            for batch_idx, ((verb, tense), pronoun_polarity_list) in enumerate(verb_tense_groups.items()):
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
                
                print(f"\nBatch {batch_idx+1}/{len(verb_tense_groups)}: {verb.english} ({tense.value})")
                print(f"   Expected: {len(pronoun_polarity_list)} examples")
                
                # Log batch start to file
                pipeline_logger.log_batch_start(
                    batch_idx + 1, 
                    len(verb_tense_groups),
                    verb.turkish,
                    verb.english,
                    tense.value,
                    len(pronoun_polarity_list)
                )
                
                # Check if all files in this batch already exist
                if skip_existing:
                    all_exist = all(
                        check_example_exists(verb, tense, p, pol, output_dir)
                        for p, pol in pronoun_polarity_list
                    )
                    if all_exist:
                        print(f"   ⏭️  Skipping batch (all {len(pronoun_polarity_list)} files already exist)")
                        skipped_existing_count += len(pronoun_polarity_list)
                        pipeline_logger.increment_skipped()
                        continue
                
                # Track time for this batch generation
                batch_start_time = time.time()
                
                # Retry logic for validation failures
                max_batch_retries = 2
                batch_attempt = 0
                batch_generated = 0
                
                while batch_attempt <= max_batch_retries:
                    # Generate batch (pronoun=None, polarity=None triggers batch mode)
                    examples_list, prompt_tokens, completion_tokens = generate_training_example(
                        verb, tense,
                        pronoun=None,  # Batch mode
                        polarity=None,  # Batch mode
                        language_level=level,
                        config=config,
                        provider=provider,
                        rate_limiter=rate_limiter,
                        timeout_retries=timeout_retries
                    )
                    
                    # Track token usage (total and per-verb)
                    total_prompt_tokens += prompt_tokens
                    total_completion_tokens += completion_tokens
                    verb_prompt_tokens += prompt_tokens
                    verb_completion_tokens += completion_tokens
                    
                    # Save each example from the batch
                    batch_generated = 0
                    batch_failed = []
                    for example in examples_list:
                        # Determine polarity for filename
                        polarity = example.turkish_verb.polarity

                        try:
                            file_path = save_training_example(example, output_dir, polarity, verb)
                            print(f"   📝 Saved: {file_path}")
                            batch_generated += 1
                            verb_example_count += 1
                        except ValueError as e:
                            # Validation failed - collect for retry
                            batch_failed.append((example, polarity, str(e)))
                    
                    # Check if we should retry
                    expected_count = len(examples_list)
                    failure_rate = len(batch_failed) / expected_count if expected_count > 0 else 0
                    
                    if len(batch_failed) > 0 and failure_rate > 0.5 and batch_attempt < max_batch_retries:
                        # More than 50% failed and we have retries left
                        print(f"   ⚠️  {len(batch_failed)}/{expected_count} examples failed validation")
                        print(f"   🔄 Retrying batch (attempt {batch_attempt + 2}/{max_batch_retries + 1})...")
                        batch_attempt += 1
                        # Reset counters for this batch (we'll regenerate)
                        verb_example_count -= batch_generated
                        continue
                    else:
                        # Either success or acceptable failure rate or out of retries
                        if batch_failed:
                            print(f"   ⚠️  {len(batch_failed)} examples failed validation (will be skipped)")
                            for _, _, error in batch_failed[:3]:  # Show first 3 errors only
                                error_line = error.split('\n')[0]
                                print(f"      - {error_line}")
                            if len(batch_failed) > 3:
                                print(f"      ... and {len(batch_failed) - 3} more")
                        break
                
                batch_duration = time.time() - batch_start_time
                generated_count += batch_generated
                
                # Update logger
                pipeline_logger.update_stats(prompt_tokens, completion_tokens, verb.english,
                                             batch_duration, generated=True)
                
                # Show statistics
                total_tokens = prompt_tokens + completion_tokens
                cumulative = total_prompt_tokens + total_completion_tokens
                tokens_per_example = total_tokens // len(examples_list) if examples_list else 0
                print(f"   ✅ Generated {batch_generated} examples in {batch_duration:.2f}s")
                print(f"      {total_tokens:,} tokens (~{tokens_per_example:,} per example)")
                print(f"      Cumulative: {cumulative:,} tokens")
        
        else:
            # SINGLE MODE: Process each combination individually
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
                      f"({tense.value}, {pronoun.value if pronoun else 'none'}, {polarity_str})")
                
                # Check if file already exists and skip if requested
                if skip_existing and check_example_exists(verb, tense, pronoun, polarity, output_dir):
                    print("   ⏭️  Skipping (file already exists)")
                    skipped_existing_count += 1
                    pipeline_logger.increment_skipped()
                    continue
                
                # Track time for this file generation
                file_start_time = time.time()
                
                # Generate single example (returns list with 1 item)
                examples_list, prompt_tokens, completion_tokens = generate_training_example(
                    verb, tense, pronoun, polarity,
                    language_level=level,
                    config=config,
                    provider=provider,
                    rate_limiter=rate_limiter,
                    timeout_retries=timeout_retries
                )
                
                file_duration = time.time() - file_start_time
                
                # Track token usage (total and per-verb)
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
                verb_prompt_tokens += prompt_tokens
                verb_completion_tokens += completion_tokens
                
                # Save the example (list should have 1 item)
                if examples_list and len(examples_list) > 0:
                    example = examples_list[0]
                    try:
                        file_path = save_training_example(example, output_dir, polarity, verb)
                        total_tokens = prompt_tokens + completion_tokens
                        cumulative = total_prompt_tokens + total_completion_tokens
                        print(f"   📝 Saved: {file_path}")
                        print(f"      ({total_tokens:,} tokens | {file_duration:.2f}s | "
                              f"cumulative: {cumulative:,} tokens)")
                        generated_count += 1
                        verb_example_count += 1
                        
                        # Update logger with token usage, duration, and verb info
                        pipeline_logger.update_stats(prompt_tokens, completion_tokens, verb.english,
                                                     file_duration, generated=True)
                    except ValueError as e:
                        # Validation failed - log and skip
                        error_line = str(e).split('\n')[0]
                        print(f"   ⚠️  Validation failed: {error_line}")
                        skipped_count += 1
                        pipeline_logger.increment_skipped()
                else:
                    print("❌ Unexpected: got empty examples list")
                    skipped_count += 1
                    pipeline_logger.increment_skipped()
        
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
        if skipped_existing_count > 0:
            print(f"⏭️  Skipped {skipped_existing_count} existing files")
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
        default=None,
        choices=["A1", "A2", "B1", "B2"],
        help="Target language level. If not specified, generates for all levels (A1, A2, B1, B2)"
    )
    parser.add_argument(
        "--top-n-verbs",
        type=int,
        default=None,
        help="Number of top verbs to process (default: 10 if no --verbs specified)"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=1,
        help="Position in verb list to start from (1-indexed, default: 1). "
             "Use with --top-n-verbs to process a range "
             "(e.g., --start-from 11 --top-n-verbs 10 processes verbs 11-20)"
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
        choices=[t.value for t in VerbTense],
        help='Specific tenses to generate (e.g., --tenses şimdiki_zaman geçmiş_zaman emir_kipi)'
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
        choices=["openai", "claude", "gemini", "deepseek", "llama"],
        default=None,
        help='LLM provider to use: "openai", "claude", "gemini", "deepseek", or "llama" (default: uses config.toml setting)'
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip generating files that already exist"
    )
    parser.add_argument(
        "--timeout-retries",
        type=int,
        default=1,
        help="Number of times to retry on timeout errors (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Determine which levels to process
    if args.language_level is None:
        # Generate for all levels
        levels = ["A1", "A2", "B1", "B2"]
        print(f"🌍 Generating for ALL language levels: {', '.join(levels)}\n")
        process_by_verb = True  # Process verb-by-verb across all levels
    else:
        levels = [args.language_level]
        process_by_verb = False  # Single level, process normally
    
    if process_by_verb:
        # New approach: Process each verb across ALL levels before moving to next verb
        print("📋 Processing strategy: Complete each verb across all levels (A1→A2→B1→B2) before next verb\n")
        
        # Load verbs to get the list
        project_root = Path(__file__).parent.parent
        verbs_file = project_root / "data" / "input" / "verbs.csv"
        all_verbs = load_verbs_from_csv(str(verbs_file))
        
        # Determine which verbs to process
        if args.verbs:
            verbs_to_process = args.verbs
            print(f"Processing {len(verbs_to_process)} specific verbs across all levels\n")
        else:
            top_n = args.top_n_verbs if args.top_n_verbs else 10
            start_from = args.start_from
            
            # Validate and slice
            if start_from < 1:
                print("⚠️  Warning: start_from must be >= 1, using 1 instead")
                start_from = 1
            if start_from > len(all_verbs):
                print(f"❌ Error: start_from ({start_from}) exceeds total verbs ({len(all_verbs)})")
                sys.exit(1)
            
            start_idx = start_from - 1
            end_idx = start_idx + top_n
            selected_verbs = all_verbs[start_idx:end_idx]
            verbs_to_process = [v.english for v in selected_verbs]
            
            end_position = start_from + len(verbs_to_process) - 1
            print(f"Processing verbs {start_from} to {end_position} ({len(verbs_to_process)} verbs) across all levels\n")
        
        # Process each verb across all levels
        for verb_idx, verb_name in enumerate(verbs_to_process, 1):
            print(f"\n{'='*80}")
            print(f"📌 VERB {verb_idx}/{len(verbs_to_process)}: {verb_name}")
            print(f"{'='*80}")
            
            # Process this verb for each level
            for level_idx, level in enumerate(levels, 1):
                print(f"\n  📚 Level {level_idx}/{len(levels)}: {level}")
                print(f"  {'-'*76}")
                
                main(
                    language_level=level,
                    specific_verbs=[verb_name],
                    tenses=args.tenses,
                    pronouns=args.pronouns,
                    polarities=args.polarities,
                    provider=args.provider,
                    skip_existing=args.skip_existing,
                    timeout_retries=args.timeout_retries
                )
            
            print(f"\n  ✅ Completed '{verb_name}' across all {len(levels)} levels")
        
        print(f"\n{'='*80}")
        print(f"🎉 ALL DONE! Processed {len(verbs_to_process)} verbs across {len(levels)} levels")
        print(f"{'='*80}")
    
    else:
        # Original approach: Process level-by-level (for single level or backward compatibility)
        for level in levels:
            if len(levels) > 1:
                print(f"\n{'='*80}")
                print(f"📚 Processing Language Level: {level}")
                print(f"{'='*80}\n")
            
            # If specific verbs are provided, use them; otherwise use top-n
            if args.verbs:
                main(
                    language_level=level,
                    specific_verbs=args.verbs,
                    tenses=args.tenses,
                    pronouns=args.pronouns,
                    polarities=args.polarities,
                    provider=args.provider,
                    skip_existing=args.skip_existing,
                    timeout_retries=args.timeout_retries
                )
            else:
                top_n = args.top_n_verbs if args.top_n_verbs else 10
                main(
                    language_level=level,
                    top_n_verbs=top_n,
                    start_from=args.start_from,
                    tenses=args.tenses,
                    pronouns=args.pronouns,
                    polarities=args.polarities,
                    provider=args.provider,
                    skip_existing=args.skip_existing,
                    timeout_retries=args.timeout_retries
                )

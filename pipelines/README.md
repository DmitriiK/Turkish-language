# Turkish Language Training Example Generation Pipeline

This pipeline automatically generates Turkish language training examples using AI to help learners practice verb conjugations across different tenses, pronouns, and proficiency levels.

## Overview

The pipeline creates structured training examples that include:
- Correctly conjugated Turkish verbs
- Equivalent sentences in English, Russian, and Turkish
- Fill-in-the-blank exercises
- Vocabulary appropriate for specific language levels (A1-B2)

## Files

### Core Pipeline Files

- **`create_traing_example.py`** - Main pipeline script for generating training examples
- **`consolidate_training_examples.py`** - Utility to merge individual JSON files into consolidated collections
- **`grammer_metadata.py`** - Grammar definitions and data models

### Supporting Files

- **`../prompts/create_training_example.prompt.md`** - AI prompt template
- **`../data/input/verbs.csv`** - Source verb list (300 most common verbs)

## Features

### Language Level Support
- **A1**: Basic present, past, and simple future tenses
- **A2**: Adds imperatives, necessity, and ability forms
- **B1**: Includes conditional, optative, and participial forms
- **B2**: Advanced tenses and complex grammatical structures

### Verb Form Handling
The pipeline correctly handles two types of verb forms:
1. **Forms WITH pronouns**: Generate 6 combinations (ben, sen, o, biz, siz, onlar)
2. **Forms WITHOUT pronouns**: Generate 1 combination (imperatives, participles, etc.)

Examples of forms without pronouns:
- `emir_kipi` (Imperatives): "Yap!" (Do!)
- `gereklilik_kipi` (Necessity): "Yapmam lazım" (I need to do)
- `sıfat_fiil` (Participles): "yapan" (doing/who does)

### Smart Vocabulary Selection
- Uses vocabulary appropriate for the target language level
- Avoids complex grammar beyond the learner's proficiency
- Creates contextually relevant and natural sentences

## Installation

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)

### Setup
1. **Create and activate virtual environment:**
   ```bash
   cd /path/to/Turkish-language
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install langchain langchain-google-genai python-dotenv pydantic
   ```

3. **Set up API key:**
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

## API Rate Limits & Quota Management

The pipeline uses the Google Gemini API and automatically handles rate limits and quota restrictions.

### Free Tier Limits (Gemini 2.0 Flash)

| Limit Type | Free Tier | Tier 1 (Paid) |
|------------|-----------|---------------|
| **Requests per minute (RPM)** | 15 | 200 |
| **Tokens per minute (TPM)** | 1,000,000 | 4,000,000 |
| **Requests per day (RPD)** | **200** | **10,000** |

**Important Notes:**
- Daily quota resets at **midnight Pacific Time** (PDT/PST)
- Rate limits are per project, not per API key
- The pipeline is configured for **8 RPM** (conservative, below the 15 RPM limit)

### Automatic Rate Limit Handling

The pipeline includes intelligent retry logic:

**1. Per-Minute Rate Limits:**
- ✅ Automatically spaces requests (~7.5s between calls)
- ✅ Extracts `retry_delay` from API error responses
- ✅ Retries up to 3 times with exponential backoff
- ✅ Displays wait times in real-time

**2. Daily Quota Limits:**
- ✅ Detects daily quota exhaustion
- ✅ **Immediately stops pipeline** when daily limit is reached (no wasted attempts)
- ✅ Preserves all successfully generated examples
- ✅ Can resume next day using `--skip-existing` flag to continue from where it left off
- ✅ Displays exact token usage before stopping

### Example Output During Rate Limiting

```
Processing 121/360: to say (geçmiş_zaman, ben, positive)
   ⏳ Rate limit: waiting 2.7s...
   📝 Prompt size: 5775 chars (~1443 tokens estimated)
   ⚠️  Rate limit hit (attempt 1/4)
   ⏸️  Rate limit exceeded, waiting 29s before retry...
   ⏳ Rate limit: waiting 7.5s...
   📝 Prompt size: 5775 chars (~1443 tokens estimated)
   📊 Tokens: 1576 input + 294 output = 1870 total
   ✅ Saved (1,870 tokens | cumulative: 225,089 tokens)
```

### Daily Quota Exhausted

```
   ❌ FATAL: Daily quota limit reached!
   📊 You've hit the Gemini API daily quota limit.
   💡 Wait 24 hours or upgrade to paid tier for higher limits.
RuntimeError: Daily quota limit reached. Cannot continue.
```

### Token Consumption Estimates

**Per Example:**
- Input tokens: ~1,577 (prompt template)
- Output tokens: ~270 (structured response)
- **Total: ~1,850 tokens per example**

**For Common Scenarios:**
- **10 verbs × 36 examples** = 360 total examples ≈ **666,000 tokens** ≈ **~180 requests** (hits daily limit)
- **5 verbs × 36 examples** = 180 total examples ≈ **333,000 tokens** ≈ **~90 requests** ✅ (within daily limit)
- **3 verbs × 36 examples** = 108 total examples ≈ **200,000 tokens** ≈ **~54 requests** ✅ (within daily limit)

### Recommended Workflow for Free Tier

**Option 1: Process in Batches with Skip-Existing**
```bash
# Day 1: Start processing 10 verbs, may hit daily limit partway through
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider gemini

# Day 2: Resume from where you left off (skips already generated files)
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider gemini --skip-existing

# Day 3: Continue until all combinations are complete
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider gemini --skip-existing
```

**Option 2: Process in Smaller Chunks Using --start-from**
```bash
# Day 1: Process verbs 1-5
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 5

# Day 2: Process verbs 6-10
python pipelines/create_traing_example.py --language-level A1 --start-from 6 --top-n-verbs 5

# Day 3: Process verbs 11-15
python pipelines/create_traing_example.py --language-level A1 --start-from 11 --top-n-verbs 5

# Day 4: Process verbs 16-20
python pipelines/create_traing_example.py --language-level A1 --start-from 16 --top-n-verbs 5
```

**Option 3: Filter by Specific Combinations**
```bash
# Only present tense, save quota for other verbs
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10 \
  --tenses şimdiki_zaman geniş_zaman

# Only specific pronouns
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10 \
  --pronouns ben sen o
```

**Option 4: Switch Providers**
```bash
# Use Azure until daily limit, then switch to Gemini
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider azure

# When Azure hits limit, continue with Gemini (skip existing files)
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider gemini --skip-existing
```

**Option 5: Upgrade to Paid Tier**
- Link Cloud Billing account in [AI Studio](https://aistudio.google.com/api-keys)
- Get 10,000 requests/day (50x more)
- Cost: ~$0.06-0.20 for 360 examples
- Process all verbs in one run

### Configuration

Rate limits are configurable in `config.toml`:

```toml
[rate_limits]
gemini = 8    # Requests per minute (conservative for free tier)
azure = 50    # Requests per minute (for paid tier)

[retry]
max_retries = 3  # Number of retry attempts for rate limit errors
```

### Monitoring Your Usage

Track your API usage at:
- [AI Studio Usage Dashboard](https://aistudio.google.com/usage?timeRange=last-28-days&tab=rate-limit)
- View active rate limits and quota consumption
- Monitor requests per day, minute, and tokens used

## Usage

### Command Line Interface

**Basic usage (default: A2 level, top 10 verbs):**
```bash
python pipelines/create_traing_example.py
```

**Custom parameters:**
```bash
# Process top 5 verbs at A1 level
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 5

# Process top 20 verbs at B1 level  
python pipelines/create_traing_example.py --language-level B1 --top-n-verbs 20

# Process verbs 11-20 (batch processing strategy)
python pipelines/create_traing_example.py --language-level A1 --start-from 11 --top-n-verbs 10

# Process verbs 51-100 at B2 level
python pipelines/create_traing_example.py --language-level B2 --start-from 51 --top-n-verbs 50

# Use Gemini provider
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider gemini

# Use Azure OpenAI provider
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider azure

# Skip existing files (useful for resuming after hitting rate limits)
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 10 --provider gemini --skip-existing
```

**Filter by specific combinations:**
```bash
# Only specific tenses
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10 \
  --tenses şimdiki_zaman geniş_zaman

# Only specific pronouns
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10 \
  --pronouns ben sen o

# Only positive or negative polarity
python pipelines/create_traing_example.py --language-level B1 --top-n-verbs 5 \
  --polarities positive

# Specific verbs only
python pipelines/create_traing_example.py --language-level A2 \
  --verbs "to be" "to have" "to do"
```

**All available options:**
```bash
python pipelines/create_traing_example.py --help
```

### Programmatic Usage

```python
from pipelines.create_traing_example import main

# Generate examples for top 15 verbs at A2 level
main(language_level="A2", top_n_verbs=15)
```

### Parameters

- `--language-level` / `language_level`: Target proficiency level
  - Options: `A1`, `A2`, `B1`, `B2`
  - Default: `A2`

- `--top-n-verbs` / `top_n_verbs`: Number of most common verbs to process
  - Type: Integer
  - Default: `10`
  - Range: 1-300 (based on available verbs in CSV)

- `--start-from`: Position in verb list to start from (use with `--top-n-verbs`)
  - Type: Integer
  - Default: `1` (1-indexed)
  - Range: 1-300
  - Example: `--start-from 11 --top-n-verbs 10` processes verbs 11-20
  - Use case: Process verbs in batches to manage daily quota limits

- `--verbs`: Specific verbs to process (instead of top-n)
  - Type: List of strings
  - Example: `--verbs "to be" "to have" "to do"`

- `--tenses`: Filter to specific tenses only
  - Options: `şimdiki_zaman`, `geçmiş_zaman`, `geniş_zaman`, etc.
  - Example: `--tenses şimdiki_zaman geçmiş_zaman`

- `--pronouns`: Filter to specific pronouns only
  - Options: `ben`, `sen`, `o`, `biz`, `siz`, `onlar`
  - Example: `--pronouns ben sen o`

- `--polarities`: Filter to specific polarities only
  - Options: `positive`, `negative`
  - Example: `--polarities positive`

- `--provider`: Choose LLM provider
  - Options: `gemini`, `azure`
  - Default: Uses value from `config.toml`

- `--skip-existing`: Skip generating files that already exist
  - Type: Boolean flag (no value needed)
  - Useful for resuming after hitting rate limits or errors
  - Example: `--skip-existing`

## Output Structure

Generated files are saved in `/data/output/training_examples_for_verbs/` with the following structure:

```
data/output/training_examples_for_verbs/
├── to_be/
│   ├── ben_olmak_şimdiki_zaman.json
│   ├── sen_olmak_şimdiki_zaman.json
│   ├── o_olmak_şimdiki_zaman.json
│   ├── biz_olmak_şimdiki_zaman.json
│   ├── siz_olmak_şimdiki_zaman.json
│   ├── onlar_olmak_şimdiki_zaman.json
│   ├── none_olmak_emir_kipi.json
│   └── ...
├── to_have/
│   └── ...
```

### File Naming Convention
`{pronoun}_{verb_infinitive}_{verb_tense}.json`

- **pronoun**: `ben`, `sen`, `o`, `biz`, `siz`, `onlar`, or `none` (for forms without pronouns)
- **verb_infinitive**: Turkish infinitive form (e.g., `olmak`, `yapmak`)
- **verb_tense**: Grammatical tense identifier (e.g., `şimdiki_zaman`, `emir_kipi`)

### JSON Structure

Each generated file contains:

```json
{
  "verb_english": "to be",
  "verb_infinitive": "olmak",
  "conjugated_verb": "oluyorum",
  "verb_tense": "şimdiki_zaman",
  "personal_pronoun": "ben",
  "english_example_sentence": "I am happy today.",
  "russian_example_sentence": "Я сегодня счастлив.",
  "turkish_example_sentence": "Ben bugün mutluyum."
}
```

## Grammar Metadata

The pipeline uses comprehensive grammar definitions in `grammer_metadata.py`:

### Verb Tenses Supported

**Present Forms:**
- `şimdiki_zaman` - Present continuous (yapıyorum)
- `geniş_zaman` - Simple present (yaparım)

**Past Forms:**
- `geçmiş_zaman` - Simple past (yaptım)

**Future Forms:**
- `gelecek_zaman` - Future tense (yapacağım)

**Modal Forms:**
- `emir_kipi` - Imperative (yap!)
- `istek_kipi` - Optative (yapayım)
- `şart_kipi` - Conditional (yapsam)

**And 11 more advanced forms...**

### Personal Pronouns
- `ben` (I) - 1st person singular
- `sen` (you) - 2nd person singular  
- `o` (he/she/it) - 3rd person singular
- `biz` (we) - 1st person plural
- `siz` (you) - 2nd person plural
- `onlar` (they) - 3rd person plural

## Examples

### Sample Output

For verb "yapmak" (to do) at A2 level:

**With Pronouns (şimdiki_zaman):**
```json
{
  "verb_english": "do",
  "verb_infinitive": "yapmak", 
  "conjugated_verb": "yapıyorum",
  "verb_tense": "şimdiki_zaman",
  "personal_pronoun": "ben",
  "english_example_sentence": "I am doing my homework.",
  "russian_example_sentence": "Я делаю домашнее задание.",
  "turkish_example_sentence": "Ben ödevimi yapıyorum."
}
```

**Without Pronouns (emir_kipi):**
```json
{
  "verb_english": "to do",
  "verb_infinitive": "yapmak",
  "conjugated_verb": "yap",
  "verb_tense": "emir_kipi", 
  "personal_pronoun": null,
  "english_example_sentence": "Do your homework!",
  "russian_example_sentence": "Делай домашнее задание!",
  "turkish_example_sentence": "Ödevini yap!",

}
```

### Statistics for Different Levels

**A1 Level:** 18 combinations per verb
- 3 verb forms × 6 pronouns = 18 total

**A2 Level:** 44 combinations per verb  
- 7 verb forms with pronouns × 6 = 42
- 2 verb forms without pronouns × 1 = 2
- Total: 44 combinations

**B1 Level:** 74 combinations per verb

**B2 Level:** 98 combinations per verb

## Advanced Features

### Consolidating Training Examples

The `consolidate_training_examples.py` script allows you to merge individual JSON training example files into a single consolidated JSON file. This is useful for:
- Creating training datasets for machine learning models
- Bulk data analysis and processing
- Easier distribution and sharing of training data
- Integration with other tools and systems

**Basic Usage:**
```bash
# Consolidate first 10 verbs
python pipelines/consolidate_training_examples.py --top-n-verbs 10

# Consolidate verbs 51-70
python pipelines/consolidate_training_examples.py --start-from 51 --top-n-verbs 20

# Consolidate specific verbs
python pipelines/consolidate_training_examples.py --verbs "be,do,have,say"

# Custom output file
python pipelines/consolidate_training_examples.py --start-from 1 --top-n-verbs 50 --output my_examples.json
```

**Parameters:**
- `--start-from` - Starting position in verb list (1-indexed, default: 1)
- `--top-n-verbs` - Number of verbs to process from start position
- `--verbs` - Comma-separated list of specific verbs to consolidate
- `--output` - Custom output file path (default: auto-generated)

**Output Format:**
```json
{
  "metadata": {
    "total_verbs": 3,
    "verbs": ["be", "do", "say"],
    "total_examples": 546
  },
  "examples": [
    {
      "verb_rank": 1,
      "verb_english": "be",
      "verb_russian": "быть",
      "verb_infinitive": "olmak",
      "turkish_verb": {
        "verb_full": "oluyorum",
        "root": "ol",
        "tense_affix": "uyor",
        "verb_tense": "şimdiki_zaman",
        "personal_pronoun": "ben",
        "personal_affix": "um",
        "polarity": "positive",
        "negative_affix": null
      },
      "english_example_sentence": "I am happy today",
      "russian_example_sentence": "Я сегодня счастлив",
      "turkish_example_sentence": "Ben bugün mutluyum",
      "turkish_example_sentence_with_blank": "Ben bugün ______"
    }
    // ... more examples
  ]
}
```

**Statistics:**
- Average of ~182 examples per verb (all tenses × pronouns × polarities × levels)
- File sizes: ~420 KB for 3 verbs, ~770 KB for 5 verbs
- Handles special characters in verb names (e.g., "set (put, place)")

### LangChain Integration
- Uses LangChain for robust prompt management
- Structured output parsing with Pydantic models
- Better error handling and retry logic

### Intelligent Filtering
- Automatically filters verb forms by language level
- Ensures vocabulary matches learner proficiency
- Maintains grammatical accuracy across all forms

### Extensible Design
- Easy to add new verb tenses
- Configurable language levels
- Modular prompt templates


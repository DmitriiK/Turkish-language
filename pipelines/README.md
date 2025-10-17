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

- **`create_traing_example.py`** - Main pipeline script
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
  "verb_english": "to do",
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


# Turkish Verb Learning App 🇹🇷

An interactive web application for mastering Turkish verb conjugations with AI-generated training examples, progressive feedback, and multi-language support.

## 🌐 Live Demo

**Try it now:** [https://dmitriik.github.io/Turkish-language/](https://dmitriik.github.io/Turkish-language/)

## 📚 Additional Resources

- [Turkish Grammar Reference Guide](./TURKISH_GRAMMAR_GUIDE.md) - Comprehensive grammar cheat sheet
- [Deployment Guide](./DEPLOYMENT.md) - Instructions for deploying to GitHub Pages

---

## 📖 About

A comprehensive system for learning Turkish grammar forms and verb conjugations, featuring an AI-powered training example generator and a modern React frontend application.

## 🚀 Quick Start

### Frontend Application (React)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Backend Pipeline (Python)
```bash
# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install langchain langchain-google-genai python-dotenv pydantic

# Configure API key (create .env file)
echo "GEMINI_API_KEY=your_key_here" > .env

# Generate training examples
python pipelines/create_traing_example.py --language-level A2 --top-n-verbs 5
```

## 📁 Project Structure

```
Turkish-language/
├── frontend/                 # React web application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── types/           # TypeScript definitions
│   │   ├── utils/           # Utility functions
│   │   └── App.tsx         # Main application
│   ├── public/             
│   │   └── data/           # Symlinked training data
│   ├── package.json
│   └── vite.config.ts
├── pipelines/               # AI training data generation
│   ├── create_traing_example.py
│   ├── grammer_metadata.py
│   └── README.md
├── data/
│   ├── input/
│   │   └── verbs.csv       # 300 most common Turkish verbs
│   └── output/
│       └── training_examples_for_verbs/  # Generated examples
├── prompts/                # AI prompt templates
├── tests/                  # Test suite
└── config.toml            # Configuration
```

## 🎯 Features

### Interactive Learning App
- **Progressive Feedback**: Get checkmarks for verb roots, tense affixes, personal affixes, and complete sentences
- **Multiple Learning Directions**: English↔Turkish, Russian↔Turkish
- **Smart Navigation**: Browse by verb rank, tense, or pronoun
- **Progress Tracking**: Monitor streaks and accuracy
- **Responsive Design**: Works on desktop and mobile

### AI-Powered Content Generation
- **Structured Output**: Generates grammatically correct Turkish verb conjugations
- **Multi-language Support**: Creates examples in English, Russian, and Turkish
- **Language Level Awareness**: Adapts vocabulary complexity (A1-B2)
- **Comprehensive Coverage**: 18+ verb tenses and forms

## 🛠️ Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Framer Motion (animations)

**Backend:**
- Python 3.12+
- LangChain (AI framework)
- Pydantic (data validation)
- Azure OpenAI / Google Gemini

## 📚 Learning Content

### Verb Coverage
- 300 most common Turkish verbs
- All major tenses (present, past, future, conditional, etc.)
- 6 personal pronouns + impersonal forms
- Language levels A1 through B2

### Grammar Topics Covered
- Verb conjugations and affixes
- Vowel and consonant harmony
- Personal pronouns and their usage
- Tense formation patterns
- Progressive feedback on accuracy

## 🎓 Usage Examples

### Learning Turkish Verbs
1. Select learning direction (e.g., "English → Turkish")
2. View English verb and sentence: "I am reading" → "Ben kitap okuyorum"
3. Type the Turkish translation
4. Get progressive feedback:
   - ✅ Verb root "oku" identified
   - ✅ Present tense affix "uyor" correct
   - ✅ Personal affix "um" correct
   - ✅ Complete sentence perfect!

### Generating Training Data

#### Basic Usage
```bash
# Generate A1 level examples for top 10 verbs
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10

# Generate B2 level examples for specific verbs
python pipelines/create_traing_example.py --language-level B2 --verbs "to be" "to do" "to go"

# Generate examples for specific tenses only
python pipelines/create_traing_example.py --tenses şimdiki_zaman geçmiş_zaman

# Generate for specific pronouns and polarities
python pipelines/create_traing_example.py --pronouns ben sen --polarities positive

# Skip already generated files
python pipelines/create_traing_example.py --skip-existing
```

#### Generation Modes

The pipeline supports two modes for efficient LLM usage:

**1. Batch Mode** (Default - Most Efficient)
- Generates all pronoun×polarity combinations in a single LLM call
- **6.5x more token-efficient** than single mode
- Automatically triggered when no `--pronouns` or `--polarities` filters specified
- Example: ~666 tokens per example vs ~4,350 in single mode

```bash
# Batch mode: generates 12 examples per verb+tense (6 pronouns × 2 polarities)
python pipelines/create_traing_example.py --language-level A2 --top-n-verbs 5
```

**2. Single Mode**
- Generates one example per LLM call
- Used when filtering by specific pronouns or polarities
- More granular control but higher token usage

```bash
# Single mode: generate only positive examples for "ben" pronoun
python pipelines/create_traing_example.py --pronouns ben --polarities positive
```

#### Provider Options

Choose from multiple LLM providers (configured in `config.toml`):

```bash
# Use Claude (Anthropic)
python pipelines/create_traing_example.py --provider claude

# Use OpenAI GPT-4
python pipelines/create_traing_example.py --provider openai

# Use Google Gemini
python pipelines/create_traing_example.py --provider gemini

# Use DeepSeek
python pipelines/create_traing_example.py --provider deepseek
```

## 📊 Pipeline Logging & Monitoring

The pipeline creates **two log files** in the `logs/` directory for comprehensive tracking:

### 1. Pipeline Log (`pipeline_log_YYYYMMDD_HHMMSS.txt`)
High-level execution summary with:
- Start/end timestamps and total duration
- Input parameters (language level, verbs, filters)
- Model configuration and temperature settings
- Statistics: processed verbs, created/skipped files
- Token usage: total input/output tokens, average per file
- Performance metrics: average/min/max generation time
- Per-verb summaries during execution
- Error details if pipeline fails

**Example output:**
```
================================================================================
TURKISH LANGUAGE TRAINING PIPELINE LOG
================================================================================

Start Time: 2025-11-13 21:57:27
Model: CLAUDE - anthropic.claude-haiku-4-5-20251001-v1:0

Input Arguments:
  language_level: B2
  top_n_verbs: None
  specific_verbs: ['say']
  pronouns: ['ben']
  polarities: ['positive']
  ...

Verb: say
  Files Created: 14
  Tokens Used: 60,911 (56,234 in + 4,677 out)

================================================================================
PIPELINE EXECUTION SUMMARY
================================================================================

Status: COMPLETED
Duration: 0:05:23

Statistics:
  Processed Verbs: 1
  Created Files: 14
  Skipped Files: 0

Token Usage:
  Input Tokens (Prompt): 56,234
  Output Tokens (Completion): 4,677
  Total Tokens: 60,911
  Average Tokens per File: 4,350
```

### 2. LLM Calls Log (`llm_calls_YYYYMMDD_HHMMSS.csv`)
**NEW!** Detailed CSV log of every LLM API call with:

| Column | Description | Example |
|--------|-------------|---------|
| `timestamp` | Date and time of the call | `2025-11-13 21:57:30` |
| `model_name` | Provider and model used | `CLAUDE - anthropic.claude-haiku-4-5-20251001-v1:0` |
| `prompt_tokens` | Number of input tokens | `5234` |
| `completion_tokens` | Number of output tokens | `1567` |
| `total_tokens` | Sum of input + output | `6801` |
| `duration_seconds` | API call duration | `3.45` |
| `error` | Error message (if any) | Empty for success |

**Use cases:**
- **Cost analysis**: Calculate exact API costs based on token usage
- **Performance monitoring**: Track API response times
- **Error tracking**: Identify and debug failed calls
- **Efficiency comparison**: Compare batch vs single mode token usage
- **Retry analysis**: See which calls required retries

**Example CSV:**
```csv
timestamp,model_name,prompt_tokens,completion_tokens,total_tokens,duration_seconds,error
2025-11-13 21:57:30,CLAUDE - anthropic.claude-haiku-4-5-20251001-v1:0,5234,1567,6801,3.45,
2025-11-13 21:57:35,CLAUDE - anthropic.claude-haiku-4-5-20251001-v1:0,5234,1589,6823,2.98,
2025-11-13 21:58:15,CLAUDE - anthropic.claude-haiku-4-5-20251001-v1:0,0,0,0,1.23,Status 429: Rate limit exceeded
```

**Analyze logs with Python:**
```python
import pandas as pd

# Load LLM call log
df = pd.read_csv('logs/llm_calls_20251113_215727.csv')

# Calculate total cost (example: Claude Haiku pricing)
input_cost = df['prompt_tokens'].sum() / 1_000_000 * 0.25  # $0.25 per 1M tokens
output_cost = df['completion_tokens'].sum() / 1_000_000 * 1.25  # $1.25 per 1M tokens
print(f"Total cost: ${input_cost + output_cost:.2f}")

# Performance metrics
df['duration_seconds'] = df['duration_seconds'].astype(float)
print(f"Average API latency: {df['duration_seconds'].mean():.2f}s")
print(f"Total API time: {df['duration_seconds'].sum():.2f}s")

# Error rate
errors = df[df['error'] != '']
print(f"Success rate: {(len(df) - len(errors)) / len(df) * 100:.1f}%")
```

### Logging Behavior
- **Automatic**: All LLM calls logged automatically
- **Real-time**: Each call flushed to disk immediately
- **Error-safe**: Failed calls logged with error details
- **Retry-aware**: Retry attempts logged as separate entries
- **Cleanup**: Files properly closed on exit (even with Ctrl+C)

## 🔧 Development Setup

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- Google Gemini or Azure OpenAI API key

### Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd Turkish-language

# Frontend setup
cd frontend
npm install
npm run dev

# Backend setup (in new terminal)
cd ..
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
```

## 🚀 Deployment

### Frontend (Static Hosting)
```bash
cd frontend
npm run build
# Deploy 'dist' folder to Vercel, Netlify, etc.
```

### Backend (Cloud Functions)
- Deploy as serverless functions
- Set environment variables for API keys
- Configure CORS for frontend access

## 📈 Performance

- **Fast Loading**: Optimized bundle sizes with code splitting
- **Efficient Data**: JSON-based training examples with caching
- **Responsive UI**: 60fps animations with Framer Motion
- **Smart Caching**: Reduces API calls and improves UX

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices
- Write tests for new features
- Use conventional commit messages
- Ensure responsive design
- Maintain accessibility standards

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Turkish language grammar resources
- OpenAI/Google for AI capabilities
- React and TypeScript communities
- Contributors and language learners

---


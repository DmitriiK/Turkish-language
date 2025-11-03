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
```bash
# Generate A1 level examples for top 10 verbs
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10

# Generate B2 level examples for top 50 verbs  
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 50
```

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


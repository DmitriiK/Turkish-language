# Turkish Verb Learning App - Frontend

A modern React-based frontend application for learning Turkish verb conjugations with interactive exercises.

## 🚀 Features

- **Interactive Learning Cards**: Practice verb conjugations with progressive feedback
- **Multiple Learning Directions**: 
  - English → Turkish
  - Russian → Turkish
  - Turkish → English  
  - Turkish → Russian
- **Smart Navigation**: Navigate by verb, tense, or pronoun
- **Progress Tracking**: Monitor your learning progress and streaks
- **Responsive Design**: Works perfectly on desktop and mobile
- **Real-time Feedback**: Get instant feedback on verb roots, affixes, and complete sentences

## 🛠️ Tech Stack

- **React 18** with TypeScript for type safety
- **Vite** for fast development and building
- **Tailwind CSS** for modern, responsive styling
- **Framer Motion** for smooth animations
- **Lucide React** for beautiful icons

## 📦 Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🏗️ Project Structure

```
frontend/
├── public/
│   └── data/                 # Training data (symlinked from parent)
├── src/
│   ├── components/           # React components
│   │   ├── LearningCard.tsx  # Main learning interface
│   │   ├── NavigationControls.tsx
│   │   └── DirectionControls.tsx
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   │   └── dataLoader.ts    # Data loading logic
│   ├── hooks/               # Custom React hooks
│   ├── App.tsx              # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🎯 How It Works

### Learning Process

1. **Select Learning Direction**: Choose which language pair to practice
2. **View Source Content**: See the verb and example sentence in the source language
3. **Input Translation**: Type the translation in the target language
4. **Progressive Feedback**: Get checkmarks for correct parts:
   - ✅ Verb root identified
   - ✅ Tense affix correct
   - ✅ Personal affix correct  
   - ✅ Complete sentence perfect
5. **Navigate**: Move to next pronoun, tense, or verb

### Data Structure

The app loads training examples from JSON files with this structure:

```json
{
  "verb_rank": 1,
  "verb_english": "to be",
  "verb_russian": "быть", 
  "verb_infinitive": "olmak",
  "turkish_verb": {
    "verb_full": "oluyorum",
    "root": "ol",
    "tense_affix": "uyor",
    "verb_tense": "şimdiki_zaman",
    "personal_pronoun": "ben",
    "personal_affix": "um"
  },
  "language_level": "A1",
  "english_example_sentence": "I am becoming happy.",
  "russian_example_sentence": "Я становлюсь счастливым.",
  "turkish_example_sentence": "Ben mutlu oluyorum."
}
```

## 🎨 Design Philosophy

- **Progressive Disclosure**: Show information when needed
- **Immediate Feedback**: Instant validation and encouragement
- **Responsive First**: Mobile-friendly design with touch interactions
- **Accessibility**: Keyboard navigation and screen reader support
- **Performance**: Optimized loading and smooth animations

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production  
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality
- `npm run type-check` - Run TypeScript compiler checks

### Code Quality

- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting
- Strict mode enabled

## 🚀 Deployment

The app can be deployed to any static hosting service:

```bash
# Build the project
npm run build

# The 'dist' folder contains the production build
# Deploy the contents of 'dist' to your hosting service
```

### Recommended Hosting

- **Vercel**: Zero-config deployment with `vercel` CLI
- **Netlify**: Drag-and-drop the `dist` folder
- **GitHub Pages**: Use GitHub Actions for automatic deployment
- **Firebase Hosting**: Use `firebase deploy`

## 📱 Mobile Support

The app is fully responsive and optimized for mobile devices:

- Touch-friendly interface
- Responsive grid layouts
- Optimized font sizes
- Mobile-first CSS approach

## 🎯 Learning Paths

### Beginner (A1-A2)
- Focus on present and past tenses
- Basic pronouns (ben, sen, o)
- Common verbs (olmak, yapmak, gitmek)

### Intermediate (B1-B2)
- Advanced tenses (conditional, optative)
- All pronouns including plural forms
- Complex sentence structures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests as needed
5. Submit a pull request

## 📄 License

This project is part of the Turkish Language Learning System.
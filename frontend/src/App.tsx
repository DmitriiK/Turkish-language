import React, { useState, useEffect } from 'react';
import { LearningCard } from '@/components/LearningCard';
import { DirectionControls } from '@/components/DirectionControls';
import { dataLoader } from '@/utils/dataLoader';
import { TrainingExample, LearnDirection, ProgressState, UserProgress, LanguageLevel } from '@/types';
import { BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

const App: React.FC = () => {
  console.log('App component rendering...'); // Debug log
  
  // Core state
  const [currentExample, setCurrentExample] = useState<TrainingExample | null>(null);
  const [direction, setDirection] = useState<LearnDirection>('english-to-turkish');
  const [languageLevel, setLanguageLevel] = useState<LanguageLevel>('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Navigation state
  const [currentVerb, setCurrentVerb] = useState('be');
  const [currentVerbDisplay, setCurrentVerbDisplay] = useState('be'); // Display label for the verb
  const [currentTense, setCurrentTense] = useState('şimdiki_zaman');
  const [currentPronoun, setCurrentPronoun] = useState<string | null>('ben');
  const [currentPolarity, setCurrentPolarity] = useState<'positive' | 'negative'>('positive');
  const [currentRank, setCurrentRank] = useState(1);
  
  // Progress tracking
  const [progress, setProgress] = useState<ProgressState>({
    verbRoot: false,
    negativeAffix: false,
    tenseAffix: false,
    personalAffix: false,
    fullSentence: false
  });
  
  const [userProgress, setUserProgress] = useState<UserProgress>({
    correctAnswers: 0,
    totalAttempts: 0,
    currentStreak: 0,
    bestStreak: 0,
    completedExamples: new Set<string>()
  });

  // Load current example
  const loadCurrentExample = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading example: verb="${currentVerb}", pronoun="${currentPronoun}", tense="${currentTense}", polarity="${currentPolarity}"`);
      
      const example = await dataLoader.loadTrainingExample(
        currentVerb,
        currentPronoun || 'ben',
        currentTense,
        currentPolarity
      );

      if (!example) {
        throw new Error(`No training example available for verb "${currentVerb}". This verb may not have complete data.`);
      }

      console.log('Successfully loaded example:', example.verb_english);
      
      // Update state with the actual values from the loaded example
      // This handles cases where requested pronoun/tense wasn't available
      setCurrentExample(example);
      setCurrentRank(example.verb_rank);
      
      // Update verb display based on direction
      if (direction === 'turkish-to-english' || direction === 'turkish-to-russian') {
        setCurrentVerbDisplay(example.verb_infinitive);
      } else {
        setCurrentVerbDisplay(example.verb_english.replace('to ', ''));
      }
      
      // Sync UI state with what was actually loaded
      const actualTense = example.turkish_verb.verb_tense;
      const actualPronoun = example.turkish_verb.personal_pronoun;
      const actualPolarity = example.turkish_verb.polarity;
      
      if (actualTense !== currentTense) {
        console.log(`Note: Requested tense "${currentTense}" not available, showing "${actualTense}"`);
        setCurrentTense(actualTense);
      }
      
      if (actualPronoun !== currentPronoun) {
        console.log(`Note: Requested pronoun "${currentPronoun}" not available, showing "${actualPronoun}"`);
        setCurrentPronoun(actualPronoun);
      }
      
      if (actualPolarity !== currentPolarity) {
        console.log(`Note: Requested polarity "${currentPolarity}" not available, showing "${actualPolarity}"`);
        setCurrentPolarity(actualPolarity);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load example';
      console.error('Error loading example:', errorMessage);
      setError(errorMessage);
      
      // Don't crash - keep the app running with the error state
      setCurrentExample(null);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    console.log('useEffect triggered, loading example...'); // Debug log
    loadCurrentExample();
  }, [currentVerb, currentTense, currentPronoun, currentPolarity]);

  // Navigation handlers
  const handleNextTense = async () => {
    const nextTense = await dataLoader.getNextTense(currentVerb, currentTense);
    if (nextTense) {
      setCurrentTense(nextTense);
      setCurrentPronoun('ben'); // Reset pronoun for new tense
    }
  };

  const handlePrevTense = async () => {
    const prevTense = await dataLoader.getPrevTense(currentVerb, currentTense);
    if (prevTense) {
      setCurrentTense(prevTense);
      setCurrentPronoun('ben');
    }
  };

  const handleNextPronoun = async () => {
    const nextPronoun = await dataLoader.getNextPronoun(currentVerb, currentTense, currentPronoun || '', currentPolarity);
    if (nextPronoun) {
      setCurrentPronoun(nextPronoun === 'none' ? null : nextPronoun);
    }
  };

  const handlePrevPronoun = async () => {
    const prevPronoun = await dataLoader.getPrevPronoun(currentVerb, currentTense, currentPronoun || '', currentPolarity);
    if (prevPronoun) {
      setCurrentPronoun(prevPronoun === 'none' ? null : prevPronoun);
    }
  };

  const handleNextPolarity = () => {
    setCurrentPolarity(currentPolarity === 'positive' ? 'negative' : 'positive');
  };

  const handlePrevPolarity = () => {
    setCurrentPolarity(currentPolarity === 'positive' ? 'negative' : 'positive');
  };

  // Direct navigation handlers for dropdowns
  const handleGoToVerb = (verb: string) => {
    setCurrentVerb(verb);
    setCurrentTense('şimdiki_zaman');
    setCurrentPronoun('ben');
  };

  const handleGoToTense = (tense: string) => {
    setCurrentTense(tense);
    setCurrentPronoun('ben'); // Reset to first person for new tense
  };

  const handleGoToPronoun = (pronoun: string) => {
    setCurrentPronoun(pronoun);
  };

  const handleGoToPolarity = (polarity: 'positive' | 'negative') => {
    setCurrentPolarity(polarity);
  };

  // Determine current source language
  const sourceLanguage = direction.includes('english') ? 'english' : 'russian';
  const isToTurkish = direction.includes('to-turkish');

  // Handle source language change
  const handleSourceLanguageChange = (newSource: 'english' | 'russian') => {
    const newDirection: LearnDirection = isToTurkish 
      ? `${newSource}-to-turkish` 
      : `turkish-to-${newSource}`;
    setDirection(newDirection);
  };

  const handleLevelChange = async (level: LanguageLevel) => {
    setLanguageLevel(level);
    console.log('Language level changed to:', level);
    
    // Check if current tense is available at this level
    const availableTenses = await dataLoader.getAvailableTenses(currentVerb, level);
    
    // If current tense is not available at this level, switch to the first available tense
    if (!availableTenses.includes(currentTense)) {
      if (availableTenses.length > 0) {
        const newTense = availableTenses[0];
        setCurrentTense(newTense);
        console.log(`Switching to first available tense for level ${level}: ${newTense}`);
      }
    } else {
      // Reload the current example
      loadCurrentExample();
    }
  };

  const handleProgress = (newProgress: ProgressState, wasManualInput: boolean = false) => {
    setProgress(newProgress);
    
    // Update user progress only when the full sentence is completed manually
    if (newProgress.fullSentence && !progress.fullSentence && wasManualInput && currentExample) {
      // Create a unique key for this example
      const exampleKey = `${currentExample.verb_english}-${currentExample.turkish_verb.personal_pronoun}-${currentExample.turkish_verb.verb_tense}-${currentExample.turkish_verb.polarity}`;
      
      setUserProgress(prev => {
        // Check if this is a NEW completed example
        const isNewCompletion = !prev.completedExamples.has(exampleKey);
        const newCompletedExamples = new Set(prev.completedExamples);
        newCompletedExamples.add(exampleKey);
        
        return {
          ...prev,
          correctAnswers: isNewCompletion ? prev.correctAnswers + 1 : prev.correctAnswers,
          totalAttempts: prev.totalAttempts + 1,
          currentStreak: prev.currentStreak + 1,
          bestStreak: Math.max(prev.bestStreak, prev.currentStreak + 1),
          completedExamples: newCompletedExamples
        };
      });
    }
  };

  if (loading && !currentExample) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading Turkish verb examples...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 mb-4">⚠️ Error</div>
          <div className="text-gray-700 mb-4">{error}</div>
          <button
            onClick={loadCurrentExample}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!currentExample) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-600">No training example available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col py-8 px-4">
      <div className="max-w-4xl mx-auto flex-1 w-full">
        {/* Header */}
        <motion.header 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <BookOpen className="w-8 h-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">
              Turkish Verb Learning
            </h1>
          </div>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <p className="text-gray-600 text-lg">
              Master Turkish verb conjugations with interactive exercises, native language:
            </p>
            <select
              value={sourceLanguage}
              onChange={(e) => handleSourceLanguageChange(e.target.value as 'english' | 'russian')}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="english">English</option>
              <option value="russian">Русский</option>
            </select>
          </div>
        </motion.header>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <DirectionControls
            currentDirection={direction}
            onDirectionChange={setDirection}
          />
        </motion.div>

        {/* Learning Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <LearningCard
            example={currentExample}
            direction={direction}
            onProgress={handleProgress}
            currentVerb={currentVerb}
            currentVerbDisplay={currentVerbDisplay}
            currentTense={currentTense}
            currentPronoun={currentPronoun}
            currentPolarity={currentPolarity}
            currentRank={currentRank}
            languageLevel={languageLevel}
            correctAnswers={userProgress.correctAnswers}
            isAnswered={userProgress.completedExamples.has(
              `${currentExample.verb_english}-${currentExample.turkish_verb.personal_pronoun}-${currentExample.turkish_verb.verb_tense}-${currentExample.turkish_verb.polarity}`
            )}
            onLevelChange={handleLevelChange}
            onNextTense={handleNextTense}
            onNextPronoun={handleNextPronoun}
            onNextPolarity={handleNextPolarity}
            onPrevTense={handlePrevTense}
            onPrevPronoun={handlePrevPronoun}
            onPrevPolarity={handlePrevPolarity}
            onGoToVerb={handleGoToVerb}
            onGoToTense={handleGoToTense}
            onGoToPronoun={handleGoToPronoun}
            onGoToPolarity={handleGoToPolarity}
          />
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 pt-6 border-t border-gray-200 text-center text-gray-600"
        >
        <div className="flex flex-col items-center gap-2">
          <p className="text-sm">
            Created by{' '}
            <a
              href="https://www.linkedin.com/in/dmitrii-kalmanovich-39050355/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 font-medium transition-colors"
            >
              Dmitrii Kalmanovich
            </a>
          </p>
          <a
            href="https://github.com/DmitriiK/Turkish-language"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-gray-500 hover:text-primary-600 transition-colors flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
            View on GitHub
          </a>
        </div>
      </motion.footer>
      </div>
    </div>
  );
};

export default App;
import React, { useState, useEffect } from 'react';
import { LearningCard } from '@/components/LearningCard';
import { DirectionControls } from '@/components/DirectionControls';
import { dataLoader } from '@/utils/dataLoader';
import { TrainingExample, LearnDirection, ProgressState, UserProgress, LanguageLevel } from '@/types';
import { BookOpen, Target, TrendingUp } from 'lucide-react';
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
  const [currentVerb, setCurrentVerb] = useState('to be');
  const [currentTense, setCurrentTense] = useState('şimdiki_zaman');
  const [currentPronoun, setCurrentPronoun] = useState<string | null>('ben');
  const [currentRank, setCurrentRank] = useState(1);
  
  // Progress tracking
  const [progress, setProgress] = useState<ProgressState>({
    verbRoot: false,
    tenseAffix: false,
    personalAffix: false,
    fullSentence: false
  });
  
  const [userProgress, setUserProgress] = useState<UserProgress>({
    correctAnswers: 0,
    totalAttempts: 0,
    currentStreak: 0,
    bestStreak: 0
  });

  // Load current example
  const loadCurrentExample = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading example: verb="${currentVerb}", pronoun="${currentPronoun}", tense="${currentTense}"`);
      
      const example = await dataLoader.loadTrainingExample(
        currentVerb,
        currentPronoun || 'ben',
        currentTense
      );

      if (!example) {
        throw new Error(`No training example available for verb "${currentVerb}". This verb may not have complete data.`);
      }

      console.log('Successfully loaded example:', example.verb_english);
      
      // Update state with the actual values from the loaded example
      // This handles cases where requested pronoun/tense wasn't available
      setCurrentExample(example);
      setCurrentRank(example.verb_rank);
      
      // Sync UI state with what was actually loaded
      const actualTense = example.turkish_verb.verb_tense;
      const actualPronoun = example.turkish_verb.personal_pronoun;
      
      if (actualTense !== currentTense) {
        console.log(`Note: Requested tense "${currentTense}" not available, showing "${actualTense}"`);
        setCurrentTense(actualTense);
      }
      
      if (actualPronoun !== currentPronoun) {
        console.log(`Note: Requested pronoun "${currentPronoun}" not available, showing "${actualPronoun}"`);
        setCurrentPronoun(actualPronoun);
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
  }, [currentVerb, currentTense, currentPronoun]);

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
    const nextPronoun = await dataLoader.getNextPronoun(currentVerb, currentTense, currentPronoun || '');
    if (nextPronoun) {
      setCurrentPronoun(nextPronoun === 'none' ? null : nextPronoun);
    }
  };

  const handlePrevPronoun = async () => {
    const prevPronoun = await dataLoader.getPrevPronoun(currentVerb, currentTense, currentPronoun || '');
    if (prevPronoun) {
      setCurrentPronoun(prevPronoun === 'none' ? null : prevPronoun);
    }
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

  const handleLevelChange = async (level: LanguageLevel) => {
    setLanguageLevel(level);
    // TODO: Implement level filtering when navigation index supports it
    console.log('Language level changed to:', level);
  };

  const handleProgress = (newProgress: ProgressState) => {
    setProgress(newProgress);
    
    // Update user progress when sentence is completed
    if (newProgress.fullSentence && !progress.fullSentence) {
      setUserProgress(prev => ({
        ...prev,
        correctAnswers: prev.correctAnswers + 1,
        totalAttempts: prev.totalAttempts + 1,
        currentStreak: prev.currentStreak + 1,
        bestStreak: Math.max(prev.bestStreak, prev.currentStreak + 1)
      }));
    }
  };

  const handleNext = () => {
    // Reset progress for new example
    setProgress({
      verbRoot: false,
      tenseAffix: false,
      personalAffix: false,
      fullSentence: false
    });

    // Auto-advance logic: pronoun → tense → verb
    handleNextPronoun();
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
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
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
          <p className="text-gray-600 text-lg">
            Master Turkish verb conjugations with interactive exercises
          </p>
        </motion.header>

        {/* Progress Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
        >
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-700">Correct Answers</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {userProgress.correctAnswers}
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">Current Streak</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {userProgress.currentStreak}
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-gray-700">Best Streak</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {userProgress.bestStreak}
            </div>
          </div>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <DirectionControls
            currentDirection={direction}
            onDirectionChange={setDirection}
            currentLevel={languageLevel}
            onLevelChange={handleLevelChange}
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
            onNext={handleNext}
            currentVerb={currentVerb}
            currentTense={currentTense}
            currentPronoun={currentPronoun}
            currentRank={currentRank}
            onNextTense={handleNextTense}
            onNextPronoun={handleNextPronoun}
            onPrevTense={handlePrevTense}
            onPrevPronoun={handlePrevPronoun}
            onGoToVerb={handleGoToVerb}
            onGoToTense={handleGoToTense}
            onGoToPronoun={handleGoToPronoun}
          />
        </motion.div>


      </div>
    </div>
  );
};

export default App;
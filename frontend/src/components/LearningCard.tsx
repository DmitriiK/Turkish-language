import React, { useState, useEffect } from 'react';
import { Check } from 'lucide-react';
import { TrainingExample, LearnDirection, ProgressState } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { NavigationControls } from './NavigationControls';

// Helper function to format grammar names
const formatGrammarName = (tense: string): string => {
  // Return Turkish grammar form names instead of English translations
  const tenseNames: Record<string, string> = {
    'geçmiş_zaman': 'geçmiş zaman',
    'şimdiki_zaman': 'şimdiki zaman',
    'geniş_zaman': 'geniş zaman',
    'gelecek_zaman': 'gelecek zaman',
    'şart_kipi': 'şart kipi',
    'emir_kipi': 'emir kipi'
  };
  return tenseNames[tense] || tense.replace('_', ' ');
};

// Helper function to format grammar name with level
const formatGrammarNameWithLevel = (tense: string, level: string | null): string => {
  const formattedName = formatGrammarName(tense);
  return level ? `${formattedName} (${level})` : formattedName;
};

// Helper to check if text is definitely not part of the answer
const isIncorrectText = (input: string, targetSentence: string): boolean => {
  const inputLower = input.toLowerCase().trim();
  const targetLower = targetSentence.toLowerCase();
  
  if (inputLower.length === 0) return false;
  
  // If input contains any characters from target, it might be partially correct
  const inputWords = inputLower.split(/\s+/);
  const targetWords = targetLower.split(/\s+/);
  
  // Check if any input word is completely foreign to target
  for (const inputWord of inputWords) {
    if (inputWord.length > 2) { // Only check meaningful words
      const hasPartialMatch = targetWords.some(targetWord => 
        targetWord.includes(inputWord) || inputWord.includes(targetWord)
      );
      if (!hasPartialMatch) {
        return true; // Found a word that doesn't belong
      }
    }
  }
  
  return false;
};

interface LearningCardProps {
  example: TrainingExample;
  direction: LearnDirection;
  onProgress: (progress: ProgressState) => void;
  onNext: () => void;
  // Navigation props
  currentVerb: string;
  currentVerbDisplay: string;
  currentTense: string;
  currentPronoun: string | null;
  currentPolarity: 'positive' | 'negative';
  currentRank: number;
  languageLevel?: string; // Optional language level filter
  onNextTense: () => void;
  onNextPronoun: () => void;
  onNextPolarity: () => void;
  onPrevTense: () => void;
  onPrevPronoun: () => void;
  onPrevPolarity: () => void;
  onGoToVerb: (verb: string) => void;
  onGoToTense: (tense: string) => void;
  onGoToPronoun: (pronoun: string) => void;
  onGoToPolarity: (polarity: 'positive' | 'negative') => void;
}

export const LearningCard: React.FC<LearningCardProps> = ({
  example,
  direction,
  onProgress,
  onNext,
  // Navigation props
  currentVerb,
  currentVerbDisplay,
  currentTense,
  currentPronoun,
  currentPolarity,
  currentRank,
  languageLevel,
  onNextTense,
  onNextPronoun,
  onNextPolarity,
  onPrevTense,
  onPrevPronoun,
  onPrevPolarity,
  onGoToVerb,
  onGoToTense,
  onGoToPronoun,
  onGoToPolarity
}) => {
  const [userInput, setUserInput] = useState('');
  const [progress, setProgress] = useState<ProgressState>({
    verbRoot: false,
    tenseAffix: false,
    personalAffix: false,
    fullSentence: false
  });
  const [feedback, setFeedback] = useState<string>('');
  const [inputState, setInputState] = useState<'neutral' | 'correct' | 'error'>('neutral');
  const [showComponents, setShowComponents] = useState({
    verbRoot: false,
    tenseAffix: false,
    personalAffix: false
  });
  const [tenseLevel, setTenseLevel] = useState<string | null>(null);

  // Load tense level mapping when component mounts or tense changes
  useEffect(() => {
    const loadTenseLevel = async () => {
      try {
        const response = await fetch('/data/tense_level_mapping.json');
        const mapping: Record<string, string> = await response.json();
        setTenseLevel(mapping[currentTense] || null);
      } catch (error) {
        console.error('Failed to load tense level mapping:', error);
        setTenseLevel(null);
      }
    };
    loadTenseLevel();
  }, [currentTense]);

  // Reset state when example changes
  useEffect(() => {
    setUserInput('');
    setProgress({
      verbRoot: false,
      tenseAffix: false,
      personalAffix: false,
      fullSentence: false
    });
    setShowComponents({
      verbRoot: false,
      tenseAffix: false,
      personalAffix: false
    });
    setFeedback('');
    setInputState('neutral');
  }, [example]);

  // Update parent with progress
  useEffect(() => {
    onProgress(progress);
  }, [progress, onProgress]);

  // Real-time progress checking (no feedback messages, no auto-advance)
  const checkProgressRealTime = (input: string) => {
    const inputLower = input.toLowerCase().trim();
    const newProgress = { ...progress };
    let hasChanges = false;
    
    // For Turkish target directions (learning Turkish)
    if (direction.endsWith('turkish')) {
      // Check verb root
      if (!progress.verbRoot && inputLower.includes(example.turkish_verb.root.toLowerCase())) {
        newProgress.verbRoot = true;
        hasChanges = true;
      }
      
      // Check tense affix
      if (!progress.tenseAffix && 
          example.turkish_verb.tense_affix && 
          inputLower.includes(example.turkish_verb.tense_affix.toLowerCase())) {
        newProgress.tenseAffix = true;
        hasChanges = true;
      }
      
      // Check personal affix
      if (!progress.personalAffix && 
          example.turkish_verb.personal_affix && 
          inputLower.includes(example.turkish_verb.personal_affix.toLowerCase())) {
        newProgress.personalAffix = true;
        hasChanges = true;
      }
    }
    
    // Check full sentence for all directions
    const targetSentence = getTargetSentence().toLowerCase();
    if (!progress.fullSentence && inputLower === targetSentence) {
      newProgress.fullSentence = true;
      hasChanges = true;
    }

    if (hasChanges) {
      setProgress(newProgress);
    }
  };

  // Build text content based on selected checkboxes
  const buildTextFromProgress = (progressState: ProgressState = progress) => {
    if (direction.endsWith('turkish')) {
      if (progressState.fullSentence) {
        return getTargetSentence();
      }
      
      let text = '';
      if (progressState.verbRoot) {
        text += example.turkish_verb.root;
      }
      if (progressState.tenseAffix && example.turkish_verb.tense_affix) {
        text += example.turkish_verb.tense_affix;
      }
      if (progressState.personalAffix && example.turkish_verb.personal_affix) {
        text += example.turkish_verb.personal_affix;
      }
      return text;
    } else {
      return progressState.fullSentence ? getTargetSentence() : '';
    }
  };

  const checkAnswer = () => {
    const input = userInput.toLowerCase().trim();
    const newProgress = { ...progress };
    const newShowComponents = { ...showComponents };
    let feedbackMessage = '';
    
    // For Turkish target directions (learning Turkish)
    if (direction.endsWith('turkish')) {
      // Check verb root
      if (!progress.verbRoot && input.includes(example.turkish_verb.root.toLowerCase())) {
        newProgress.verbRoot = true;
        newShowComponents.verbRoot = true;
        feedbackMessage += '✅ Verb root correct! ';
      }
      
      // Check tense affix
      if (!progress.tenseAffix && 
          example.turkish_verb.tense_affix && 
          input.includes(example.turkish_verb.tense_affix.toLowerCase())) {
        newProgress.tenseAffix = true;
        newShowComponents.tenseAffix = true;
        feedbackMessage += '✅ Tense affix correct! ';
      }
      
      // Check personal affix
      if (!progress.personalAffix && 
          example.turkish_verb.personal_affix && 
          input.includes(example.turkish_verb.personal_affix.toLowerCase())) {
        newProgress.personalAffix = true;
        newShowComponents.personalAffix = true;
        feedbackMessage += '✅ Personal affix correct! ';
      }
    }
    
    // Check full sentence for all directions
    const targetSentence = getTargetSentence().toLowerCase();
    if (!progress.fullSentence && input === targetSentence) {
      newProgress.fullSentence = true;
      feedbackMessage += '🎉 Perfect!';
      setInputState('correct');
    } else if (feedbackMessage) {
      setInputState('neutral');
    } else {
      // Check if input is definitely wrong (contains words not in target)
      if (isIncorrectText(input, targetSentence)) {
        setInputState('error');
        feedbackMessage = '❌ Some parts are incorrect. Try again...';
      } else {
        setInputState('neutral');
        feedbackMessage = '⚠️ Keep working on it...';
      }
    }

    setProgress(newProgress);
    setShowComponents(newShowComponents);
    setFeedback(feedbackMessage);

    // Auto advance if everything is complete
    if (newProgress.fullSentence) {
      setTimeout(() => {
        onNext();
      }, 2000);
    }
  };

  const getSourceContent = () => {
    switch (direction) {
      case 'english-to-turkish':
        return {
          verb: example.verb_english,
          sentence: example.english_example_sentence,
          language: 'English'
        };
      case 'russian-to-turkish':
        return {
          verb: example.verb_russian,
          sentence: example.russian_example_sentence,
          language: 'Russian'
        };
      case 'turkish-to-english':
        return {
          verb: example.verb_infinitive,
          sentence: example.turkish_example_sentence,
          language: 'Turkish'
        };
      case 'turkish-to-russian':
        return {
          verb: example.verb_infinitive,
          sentence: example.turkish_example_sentence,
          language: 'Turkish'
        };
      default:
        return {
          verb: example.verb_english,
          sentence: example.english_example_sentence,
          language: 'English'
        };
    }
  };

  const getTargetSentence = (): string => {
    switch (direction) {
      case 'english-to-turkish':
      case 'russian-to-turkish':
        return example.turkish_example_sentence;
      case 'turkish-to-english':
        return example.english_example_sentence;
      case 'turkish-to-russian':
        return example.russian_example_sentence;
      default:
        return example.turkish_example_sentence;
    }
  };

  const getTargetLanguage = (): string => {
    switch (direction) {
      case 'english-to-turkish':
      case 'russian-to-turkish':
        return 'Turkish';
      case 'turkish-to-english':
        return 'English';
      case 'turkish-to-russian':
        return 'Russian';
      default:
        return 'Turkish';
    }
  };

  const source = getSourceContent();
  const targetLanguage = getTargetLanguage();
  const isLearningTurkish = direction.endsWith('turkish');

  return (
    <div className="card max-w-6xl mx-auto animate-fade-in">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-500">
            #{example.verb_rank} • {formatGrammarNameWithLevel(example.turkish_verb.verb_tense, tenseLevel)}
          </div>
          <div className="text-sm font-medium text-primary-600">
            {source.language} → {targetLanguage}
          </div>
        </div>
        
        <div className="text-center mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="text-lg font-semibold text-gray-700 mb-2">
            {source.verb}
          </div>
          <div className="text-xl text-gray-900">
            "{source.sentence}"
          </div>
        </div>
      </div>

      {/* Main Input Section */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Translate to {targetLanguage}:
        </label>
        <div className="relative">
          <input
            type="text"
            value={userInput}
            onChange={(e) => {
              const newValue = e.target.value;
              setUserInput(newValue);
              checkProgressRealTime(newValue);
            }}
            onKeyPress={(e) => e.key === 'Enter' && checkAnswer()}
            className={clsx(
              'input text-lg',
              inputState === 'correct' && 'input-correct border-green-500 bg-green-50',
              inputState === 'error' && 'input-error border-red-500 bg-red-50'
            )}
            placeholder={`Type the ${targetLanguage.toLowerCase()} translation...`}
            autoComplete="off"
          />
        </div>
        
        <button
          onClick={checkAnswer}
          className="btn-primary mt-3 w-full"
        >
          Check Answer
        </button>
      </div>

      {/* Feedback */}
      <AnimatePresence>
        {feedback && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={clsx(
              'p-3 rounded-lg text-sm font-medium mb-4',
              progress.fullSentence 
                ? 'bg-green-100 text-green-800'
                : inputState === 'error'
                ? 'bg-red-100 text-red-800'
                : 'bg-blue-100 text-blue-800'
            )}
          >
            {feedback}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress Indicators */}
      {isLearningTurkish ? (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Progress Indicators:
          </h3>
          <div className="flex flex-wrap gap-4">
            <ProgressCheckbox
              label="Verb Root"
              checked={progress.verbRoot}
              onToggle={() => {
                const newProgress = { ...progress, verbRoot: !progress.verbRoot };
                setProgress(newProgress);
                // Update main textbox based on new progress
                setUserInput(buildTextFromProgress(newProgress));
              }}
            />
            <ProgressCheckbox
              label="Tense Affix"
              checked={progress.tenseAffix}
              onToggle={() => {
                const newProgress = { ...progress, tenseAffix: !progress.tenseAffix };
                setProgress(newProgress);
                // Update main textbox based on new progress
                setUserInput(buildTextFromProgress(newProgress));
              }}
            />
            <ProgressCheckbox
              label="Personal Affix"
              checked={progress.personalAffix}
              onToggle={() => {
                const newProgress = { ...progress, personalAffix: !progress.personalAffix };
                setProgress(newProgress);
                // Update main textbox based on new progress
                setUserInput(buildTextFromProgress(newProgress));
              }}
            />
            <ProgressCheckbox
              label="Complete Phrase"
              checked={progress.fullSentence}
              onToggle={() => {
                const isChecking = !progress.fullSentence;
                const newProgress = { 
                  ...progress, 
                  fullSentence: isChecking,
                  // If checking Complete Phrase, check all components too
                  verbRoot: isChecking ? true : progress.verbRoot,
                  tenseAffix: isChecking ? true : progress.tenseAffix,
                  personalAffix: isChecking ? true : progress.personalAffix
                };
                setProgress(newProgress);
                // Update main textbox based on new progress
                setUserInput(buildTextFromProgress(newProgress));
              }}
            />
          </div>
        </div>
      ) : (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Progress:
          </h3>
          <div className="flex items-center gap-2">
            <ProgressCheckbox
              label="Complete Answer"
              checked={progress.fullSentence}
              onToggle={() => {
                const isChecking = !progress.fullSentence;
                const newProgress = { 
                  ...progress, 
                  fullSentence: isChecking,
                  // If checking Complete Answer, check all components too (for consistency)
                  verbRoot: isChecking ? true : progress.verbRoot,
                  tenseAffix: isChecking ? true : progress.tenseAffix,
                  personalAffix: isChecking ? true : progress.personalAffix
                };
                setProgress(newProgress);
                // Update main textbox based on new progress
                setUserInput(buildTextFromProgress(newProgress));
              }}
            />
          </div>
        </div>
      )}

      {/* Navigation Controls */}
      <NavigationControls
        currentVerb={currentVerb}
        currentVerbDisplay={currentVerbDisplay}
        currentTense={currentTense}
        currentPronoun={currentPronoun}
        currentPolarity={currentPolarity}
        currentRank={currentRank}
        languageLevel={languageLevel}
        direction={direction}
        onNextTense={onNextTense}
        onNextPronoun={onNextPronoun}
        onNextPolarity={onNextPolarity}
        onPrevTense={onPrevTense}
        onPrevPronoun={onPrevPronoun}
        onPrevPolarity={onPrevPolarity}
        onGoToVerb={onGoToVerb}
        onGoToTense={onGoToTense}
        onGoToPronoun={onGoToPronoun}
        onGoToPolarity={onGoToPolarity}
      />
    </div>
  );
};

interface ProgressCheckboxProps {
  label: string;
  checked: boolean;
  onToggle?: () => void;
}

const ProgressCheckbox: React.FC<ProgressCheckboxProps> = ({
  label,
  checked,
  onToggle
}) => {
  return (
    <div className="flex items-center gap-2">
      <div 
        className={clsx(
          'w-5 h-5 border-2 rounded flex items-center justify-center transition-colors cursor-pointer hover:border-blue-400',
          checked 
            ? 'bg-green-500 border-green-500'
            : 'border-gray-300'
        )}
        onClick={onToggle}
      >
        {checked && (
          <Check className="w-3 h-3 text-white" />
        )}
      </div>
      <span 
        className="text-sm font-medium text-gray-700 cursor-pointer hover:text-blue-600" 
        onClick={onToggle}
      >
        {label}
      </span>
    </div>
  );
};
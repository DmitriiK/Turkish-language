import React, { useState, useEffect, useRef } from 'react';
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
    negativeAffix: false,
    tenseAffix: false,
    personalAffix: false,
    fullSentence: false
  });
  const [feedback, setFeedback] = useState<string>('');
  const [inputState, setInputState] = useState<'neutral' | 'correct' | 'error'>('neutral');
  const [showComponents, setShowComponents] = useState({
    verbRoot: false,
    negativeAffix: false,
    tenseAffix: false,
    personalAffix: false
  });
  const [tenseLevel, setTenseLevel] = useState<string | null>(null);
  const editableRef = useRef<HTMLDivElement>(null);

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
      negativeAffix: false,
      tenseAffix: false,
      personalAffix: false,
      fullSentence: false
    });
    setShowComponents({
      verbRoot: false,
      negativeAffix: false,
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

  // Update colored text when progress changes
  useEffect(() => {
    if (editableRef.current && document.activeElement !== editableRef.current) {
      const coloredHtml = renderColoredText();
      if (editableRef.current.innerHTML !== coloredHtml) {
        const selection = window.getSelection();
        const cursorPos = selection?.focusOffset || 0;
        editableRef.current.innerHTML = coloredHtml;
        
        // Restore cursor position
        if (selection && coloredHtml) {
          try {
            const range = document.createRange();
            const lastChild = editableRef.current.lastChild;
            if (lastChild) {
              range.setStart(lastChild, Math.min(cursorPos, lastChild.textContent?.length || 0));
              range.collapse(true);
              selection.removeAllRanges();
              selection.addRange(range);
            }
          } catch (e) {
            // Ignore cursor restoration errors
          }
        }
      }
    }
  }, [progress, userInput]);

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
      
      // Check negative affix (only for negative polarity)
      if (example.turkish_verb.polarity === 'negative' && 
          example.turkish_verb.negative_affix &&
          !progress.negativeAffix && 
          inputLower.includes(example.turkish_verb.negative_affix.toLowerCase())) {
        newProgress.negativeAffix = true;
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
      if (progressState.negativeAffix && example.turkish_verb.negative_affix) {
        text += example.turkish_verb.negative_affix;
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

  // Render colored HTML for the contenteditable div
  const renderColoredText = () => {
    // Helper to escape HTML special characters
    const escapeHtml = (text: string) => {
      return text.replace(/&/g, '&amp;')
                 .replace(/</g, '&lt;')
                 .replace(/>/g, '&gt;')
                 .replace(/"/g, '&quot;')
                 .replace(/'/g, '&#039;');
    };
    
    if (!isLearningTurkish) {
      // For non-Turkish, just return plain text
      return userInput || '';
    }

    // If no checkboxes are checked but user has typed something, just show plain text
    if (!progress.verbRoot && !progress.negativeAffix && !progress.tenseAffix && !progress.personalAffix && !progress.fullSentence) {
      return userInput || '';
    }

    // For full sentence, we need to find and color the verb within the sentence
    if (progress.fullSentence) {
      const sentence = userInput;
      const verbFull = example.turkish_verb.verb_full;
      const verbIndex = sentence.toLowerCase().indexOf(verbFull.toLowerCase());
      
      if (verbIndex === -1) {
        // Verb not found in sentence, return plain text
        return escapeHtml(sentence);
      }
      
      // Build HTML with colored verb parts
      let html = '';
      
      // Add text before verb
      html += escapeHtml(sentence.substring(0, verbIndex));
      
      // Add colored verb parts
      let verbOffset = 0;
      
      if (example.turkish_verb.root) {
        html += `<span style="color: #1d4ed8; font-weight: bold;">${escapeHtml(example.turkish_verb.root)}</span>`;
        verbOffset += example.turkish_verb.root.length;
      }
      
      if (example.turkish_verb.negative_affix) {
        html += `<span style="color: #7e22ce;">${escapeHtml(example.turkish_verb.negative_affix)}</span>`;
        verbOffset += example.turkish_verb.negative_affix.length;
      }
      
      if (example.turkish_verb.tense_affix) {
        html += `<span style="color: #c2410c;">${escapeHtml(example.turkish_verb.tense_affix)}</span>`;
        verbOffset += example.turkish_verb.tense_affix.length;
      }
      
      if (example.turkish_verb.personal_affix) {
        html += `<span style="color: #15803d;">${escapeHtml(example.turkish_verb.personal_affix)}</span>`;
        verbOffset += example.turkish_verb.personal_affix.length;
      }
      
      // Add text after verb
      html += escapeHtml(sentence.substring(verbIndex + verbFull.length));
      
      return html;
    }

    // Build colored HTML based on progress checkboxes (for partial verb)
    let html = '';
    let currentIndex = 0;
    
    if (progress.verbRoot && example.turkish_verb.root) {
      // Root in bold blue
      const rootLength = example.turkish_verb.root.length;
      html += `<span style="color: #1d4ed8; font-weight: bold;">${escapeHtml(example.turkish_verb.root)}</span>`;
      currentIndex += rootLength;
    }
    
    if (progress.negativeAffix && example.turkish_verb.negative_affix) {
      // Negative affix in purple
      const affixLength = example.turkish_verb.negative_affix.length;
      html += `<span style="color: #7e22ce;">${escapeHtml(example.turkish_verb.negative_affix)}</span>`;
      currentIndex += affixLength;
    }
    
    if (progress.tenseAffix && example.turkish_verb.tense_affix) {
      // Tense affix in orange
      const affixLength = example.turkish_verb.tense_affix.length;
      html += `<span style="color: #c2410c;">${escapeHtml(example.turkish_verb.tense_affix)}</span>`;
      currentIndex += affixLength;
    }
    
    if (progress.personalAffix && example.turkish_verb.personal_affix) {
      // Personal affix in green
      const affixLength = example.turkish_verb.personal_affix.length;
      html += `<span style="color: #15803d;">${escapeHtml(example.turkish_verb.personal_affix)}</span>`;
      currentIndex += affixLength;
    }

    // Add any remaining text that user typed beyond the verb parts
    if (userInput.length > currentIndex) {
      html += escapeHtml(userInput.substring(currentIndex));
    }

    return html || '';
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
      
      // Check negative affix (only for negative polarity)
      if (example.turkish_verb.polarity === 'negative' && 
          example.turkish_verb.negative_affix &&
          !progress.negativeAffix && 
          input.includes(example.turkish_verb.negative_affix.toLowerCase())) {
        newProgress.negativeAffix = true;
        newShowComponents.negativeAffix = true;
        feedbackMessage += '✅ Negative affix correct! ';
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
          <div
            ref={editableRef}
            contentEditable
            onInput={(e) => {
              const newValue = e.currentTarget.textContent || '';
              setUserInput(newValue);
              checkProgressRealTime(newValue);
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                checkAnswer();
              }
            }}
            className={clsx(
              'input text-lg min-h-[2.5rem] outline-none',
              inputState === 'correct' && 'input-correct border-green-500 bg-green-50',
              inputState === 'error' && 'input-error border-red-500 bg-red-50',
              !userInput && 'empty'
            )}
            data-placeholder={`Type the ${targetLanguage.toLowerCase()} translation...`}
            style={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}
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
              color="blue"
              onToggle={() => {
                const newProgress = { ...progress, verbRoot: !progress.verbRoot };
                setProgress(newProgress);
                // Update main textbox based on new progress
                setUserInput(buildTextFromProgress(newProgress));
              }}
            />
            {example.turkish_verb.polarity === 'negative' && example.turkish_verb.negative_affix && (
              <ProgressCheckbox
                label="Negative Affix"
                checked={progress.negativeAffix}
                color="purple"
                onToggle={() => {
                  const newProgress = { ...progress, negativeAffix: !progress.negativeAffix };
                  setProgress(newProgress);
                  // Update main textbox based on new progress
                  setUserInput(buildTextFromProgress(newProgress));
                }}
              />
            )}
            <ProgressCheckbox
              label="Tense Affix"
              checked={progress.tenseAffix}
              color="orange"
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
              color="green"
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
              color="gray"
              onToggle={() => {
                const isChecking = !progress.fullSentence;
                const newProgress = { 
                  ...progress, 
                  fullSentence: isChecking,
                  // If checking Complete Phrase, check all components too
                  verbRoot: isChecking ? true : progress.verbRoot,
                  negativeAffix: (isChecking && example.turkish_verb.polarity === 'negative') ? true : progress.negativeAffix,
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
                  negativeAffix: isChecking ? true : progress.negativeAffix,
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
  color?: string; // Tailwind color class (e.g., 'blue', 'purple', 'orange', 'pink')
}

const ProgressCheckbox: React.FC<ProgressCheckboxProps> = ({
  label,
  checked,
  onToggle,
  color = 'green'
}) => {
  // Define color variants for different states
  const getColorClasses = () => {
    const colorMap: Record<string, { bg: string; border: string; text: string; hover: string }> = {
      blue: { 
        bg: 'bg-blue-500', 
        border: 'border-blue-500', 
        text: 'text-blue-700',
        hover: 'hover:border-blue-400'
      },
      purple: { 
        bg: 'bg-purple-500', 
        border: 'border-purple-500', 
        text: 'text-purple-700',
        hover: 'hover:border-purple-400'
      },
      orange: { 
        bg: 'bg-orange-500', 
        border: 'border-orange-500', 
        text: 'text-orange-700',
        hover: 'hover:border-orange-400'
      },
      green: { 
        bg: 'bg-green-600', 
        border: 'border-green-600', 
        text: 'text-green-700',
        hover: 'hover:border-green-500'
      },
      gray: { 
        bg: 'bg-gray-500', 
        border: 'border-gray-500', 
        text: 'text-gray-700',
        hover: 'hover:border-gray-400'
      }
    };
    return colorMap[color] || colorMap.gray;
  };

  const colors = getColorClasses();

  return (
    <div className="flex items-center gap-2">
      <div 
        className={clsx(
          'w-5 h-5 border-2 rounded flex items-center justify-center transition-colors cursor-pointer',
          checked 
            ? `${colors.bg} ${colors.border}`
            : `border-gray-300 ${colors.hover}`
        )}
        onClick={onToggle}
      >
        {checked && (
          <Check className="w-3 h-3 text-white" />
        )}
      </div>
      <span 
        className={clsx(
          'text-sm font-medium cursor-pointer transition-colors',
          checked ? colors.text : 'text-gray-700',
          'hover:opacity-80'
        )}
        onClick={onToggle}
      >
        {label}
      </span>
    </div>
  );
};
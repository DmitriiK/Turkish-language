import React, { useState, useEffect, useRef } from 'react';
import { Check, Target, BookOpen } from 'lucide-react';
import { TrainingExample, LearnDirection, ProgressState, LANGUAGE_LEVELS, LanguageLevel } from '@/types';
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
  onProgress: (progress: ProgressState, wasManualInput?: boolean) => void;
  onNext: () => void;
  // Navigation props
  currentVerb: string;
  currentVerbDisplay: string;
  currentTense: string;
  currentPronoun: string | null;
  currentPolarity: 'positive' | 'negative';
  currentRank: number;
  languageLevel?: string; // Optional language level filter
  correctAnswers: number; // Correct answers counter
  onLevelChange: (level: LanguageLevel) => void; // Language level change handler
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
  correctAnswers,
  onLevelChange,
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
    
    if (!direction.endsWith('turkish')) {
      // For non-Turkish, just return plain text
      return userInput || '';
    }

    if (!userInput) {
      return '';
    }

    // Try to find and color the verb within the sentence
    const verbFull = example.turkish_verb.verb_full;
    const inputLower = userInput.toLowerCase();
    const verbIndex = inputLower.indexOf(verbFull.toLowerCase());
    
    if (verbIndex !== -1) {
      // Verb found in sentence - color it
      let html = '';
      
      // Add text before verb
      html += escapeHtml(userInput.substring(0, verbIndex));
      
      // Add colored verb parts
      let verbOffset = verbIndex;
      
      if (example.turkish_verb.root) {
        html += `<span style="color: #1d4ed8; font-weight: bold;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.root.length))}</span>`;
        verbOffset += example.turkish_verb.root.length;
      }
      
      if (example.turkish_verb.negative_affix) {
        html += `<span style="color: #7e22ce;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.negative_affix.length))}</span>`;
        verbOffset += example.turkish_verb.negative_affix.length;
      }
      
      if (example.turkish_verb.tense_affix) {
        html += `<span style="color: #c2410c;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.tense_affix.length))}</span>`;
        verbOffset += example.turkish_verb.tense_affix.length;
      }
      
      if (example.turkish_verb.personal_affix) {
        html += `<span style="color: #15803d;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.personal_affix.length))}</span>`;
        verbOffset += example.turkish_verb.personal_affix.length;
      }
      
      // Add text after verb
      html += escapeHtml(userInput.substring(verbIndex + verbFull.length));
      
      return html;
    }
    
    // Verb not found as complete word - try to find partial verb anywhere in the sentence
    // Build the verb parts we're looking for
    const verbParts = [];
    if (example.turkish_verb.root) {
      verbParts.push({ text: example.turkish_verb.root, color: '#1d4ed8', bold: true });
    }
    if (example.turkish_verb.negative_affix) {
      verbParts.push({ text: example.turkish_verb.negative_affix, color: '#7e22ce', bold: false });
    }
    if (example.turkish_verb.tense_affix) {
      verbParts.push({ text: example.turkish_verb.tense_affix, color: '#c2410c', bold: false });
    }
    if (example.turkish_verb.personal_affix) {
      verbParts.push({ text: example.turkish_verb.personal_affix, color: '#15803d', bold: false });
    }
    
    // Try to find where the verb starts by looking for the root
    if (verbParts.length > 0) {
      const rootPart = verbParts[0];
      const rootIndex = inputLower.indexOf(rootPart.text.toLowerCase());
      
      if (rootIndex !== -1) {
        // Found the root - try to match subsequent parts from here
        let html = '';
        let currentIndex = rootIndex;
        
        // Add text before the verb
        html += escapeHtml(userInput.substring(0, rootIndex));
        
        // Try to match each part sequentially
        for (const part of verbParts) {
          const partLower = part.text.toLowerCase();
          const remainingInput = userInput.substring(currentIndex).toLowerCase();
          
          if (remainingInput.startsWith(partLower)) {
            // This part matches - color it
            const actualText = userInput.substring(currentIndex, currentIndex + part.text.length);
            const style = part.bold 
              ? `color: ${part.color}; font-weight: bold;`
              : `color: ${part.color};`;
            html += `<span style="${style}">${escapeHtml(actualText)}</span>`;
            currentIndex += part.text.length;
          } else {
            // Part doesn't match - stop trying to match further parts
            break;
          }
        }
        
        // Add any remaining text after the verb
        if (currentIndex < userInput.length) {
          html += escapeHtml(userInput.substring(currentIndex));
        }
        
        return html;
      }
    }
    
    // No match found at all, return plain text
    return escapeHtml(userInput);
  };

  // Helper function to update colored text with cursor preservation
  const updateColoredText = () => {
    if (!editableRef.current) return;
    
    const coloredHtml = renderColoredText();
    const currentHTML = editableRef.current.innerHTML;
    
    // Skip if no change needed
    if (currentHTML === coloredHtml) return;
    
    // Save cursor position
    const selection = window.getSelection();
    let cursorOffset = 0;
    
    if (selection && selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const preCaretRange = range.cloneRange();
      preCaretRange.selectNodeContents(editableRef.current);
      preCaretRange.setEnd(range.endContainer, range.endOffset);
      cursorOffset = preCaretRange.toString().length;
    }
    
    // Update HTML
    editableRef.current.innerHTML = coloredHtml;
    
    // Restore cursor position
    if (selection && coloredHtml) {
      try {
        const range = document.createRange();
        let charCount = 0;
        let foundPosition = false;
        
        const traverseNodes = (node: Node): boolean => {
          if (node.nodeType === Node.TEXT_NODE) {
            const textLength = node.textContent?.length || 0;
            if (charCount + textLength >= cursorOffset) {
              range.setStart(node, cursorOffset - charCount);
              range.collapse(true);
              foundPosition = true;
              return true;
            }
            charCount += textLength;
          } else if (node.childNodes) {
            for (let i = 0; i < node.childNodes.length; i++) {
              if (traverseNodes(node.childNodes[i])) {
                return true;
              }
            }
          }
          return false;
        };
        
        traverseNodes(editableRef.current);
        
        if (foundPosition) {
          selection.removeAllRanges();
          selection.addRange(range);
        }
      } catch (e) {
        // Ignore cursor restoration errors
      }
    }
  };

  // Update colored text whenever userInput changes
  useEffect(() => {
    if (editableRef.current) {
      // Use requestAnimationFrame to ensure DOM is ready
      requestAnimationFrame(() => {
        updateColoredText();
      });
    }
  }, [userInput, direction]);

  // Real-time progress checking (bidirectional sync with checkboxes)
  const checkProgressRealTime = (input: string) => {
    // Remove trailing dots for comparison
    const inputTrimmed = input.trim().replace(/\.+$/, '');
    const inputLower = inputTrimmed.toLowerCase();
    const newProgress = { ...progress };
    let hasChanges = false;
    
    // For Turkish target directions (learning Turkish)
    if (direction.endsWith('turkish')) {
      // Check verb root - both enable and disable
      const hasVerbRoot = inputLower.includes(example.turkish_verb.root.toLowerCase());
      if (progress.verbRoot !== hasVerbRoot) {
        newProgress.verbRoot = hasVerbRoot;
        hasChanges = true;
      }
      
      // Check negative affix (only for negative polarity) - both enable and disable
      if (example.turkish_verb.polarity === 'negative' && example.turkish_verb.negative_affix) {
        const hasNegativeAffix = inputLower.includes(example.turkish_verb.negative_affix.toLowerCase());
        if (progress.negativeAffix !== hasNegativeAffix) {
          newProgress.negativeAffix = hasNegativeAffix;
          hasChanges = true;
        }
      }
      
      // Check tense affix - both enable and disable
      if (example.turkish_verb.tense_affix) {
        const hasTenseAffix = inputLower.includes(example.turkish_verb.tense_affix.toLowerCase());
        if (progress.tenseAffix !== hasTenseAffix) {
          newProgress.tenseAffix = hasTenseAffix;
          hasChanges = true;
        }
      }
      
      // Check personal affix - both enable and disable
      if (example.turkish_verb.personal_affix) {
        const hasPersonalAffix = inputLower.includes(example.turkish_verb.personal_affix.toLowerCase());
        if (progress.personalAffix !== hasPersonalAffix) {
          newProgress.personalAffix = hasPersonalAffix;
          hasChanges = true;
        }
      }
    }
    
    // Check full sentence for all directions (ignore trailing dots)
    const targetSentence = getTargetSentence().toLowerCase().replace(/\.+$/, '');
    const isFullSentenceMatch = inputLower === targetSentence;
    const wasFullSentenceCompleted = !progress.fullSentence && isFullSentenceMatch;
    
    if (progress.fullSentence !== isFullSentenceMatch) {
      newProgress.fullSentence = isFullSentenceMatch;
      hasChanges = true;
    }

    if (hasChanges) {
      setProgress(newProgress);
      // Notify parent - if full sentence was completed, mark as manual input
      onProgress(newProgress, wasFullSentenceCompleted);
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

  const checkAnswer = () => {
    // Remove trailing dots for comparison
    const input = userInput.trim().replace(/\.+$/, '').toLowerCase();
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
    
    // Check full sentence for all directions (ignore trailing dots)
    const targetSentence = getTargetSentence().toLowerCase().replace(/\.+$/, '');
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
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-500">
              #{example.verb_rank} • {formatGrammarNameWithLevel(example.turkish_verb.verb_tense, tenseLevel)}
            </div>
            {/* Language Level Selector */}
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-primary-600" />
              <select
                value={languageLevel || 'All'}
                onChange={(e) => onLevelChange(e.target.value as LanguageLevel)}
                className="px-2 py-1 border border-gray-300 rounded text-xs focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {LANGUAGE_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </div>
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
            suppressContentEditableWarning
            onInput={(e) => {
              // Get plain text content (this strips HTML tags)
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
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700">
              Progress Indicators:
            </h3>
            {/* Correct Answers Counter */}
            <div 
              className="bg-green-50 border-2 border-green-500 rounded-lg px-3 py-1"
              title="Correct answers entered manually"
            >
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-green-600" />
                <span className="text-xl font-bold text-green-600">
                  {correctAnswers}
                </span>
              </div>
            </div>
          </div>
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
                // Don't notify parent - this is not manual input
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
                  // Don't notify parent - this is not manual input
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
                // Don't notify parent - this is not manual input
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
                // Don't notify parent - this is not manual input
              }}
            />
            <ProgressCheckbox
              label="Complete Phrase"
              checked={progress.fullSentence}
              color="gray"
              onToggle={() => {
                const isChecking = !progress.fullSentence;
                
                if (isChecking) {
                  // If checking Complete Phrase, check all components too
                  const newProgress = { 
                    ...progress, 
                    fullSentence: true,
                    verbRoot: true,
                    negativeAffix: example.turkish_verb.polarity === 'negative' ? true : progress.negativeAffix,
                    tenseAffix: true,
                    personalAffix: true
                  };
                  setProgress(newProgress);
                  setUserInput(buildTextFromProgress(newProgress));
                } else {
                  // If unchecking Complete Phrase, uncheck all components and clear textbox
                  const newProgress = { 
                    verbRoot: false,
                    negativeAffix: false,
                    tenseAffix: false,
                    personalAffix: false,
                    fullSentence: false
                  };
                  setProgress(newProgress);
                  setUserInput('');
                }
                // Don't notify parent - this is not manual input
              }}
            />
          </div>
        </div>
      ) : (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700">
              Progress:
            </h3>
            {/* Correct Answers Counter */}
            <div 
              className="bg-green-50 border-2 border-green-500 rounded-lg px-3 py-1"
              title="Correct answers entered manually"
            >
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-green-600" />
                <span className="text-xl font-bold text-green-600">
                  {correctAnswers}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ProgressCheckbox
              label="Complete Answer"
              checked={progress.fullSentence}
              onToggle={() => {
                const isChecking = !progress.fullSentence;
                
                if (isChecking) {
                  // If checking Complete Answer, check all components too (for consistency)
                  const newProgress = { 
                    ...progress, 
                    fullSentence: true,
                    verbRoot: true,
                    negativeAffix: true,
                    tenseAffix: true,
                    personalAffix: true
                  };
                  setProgress(newProgress);
                  setUserInput(buildTextFromProgress(newProgress));
                } else {
                  // If unchecking Complete Answer, uncheck all components and clear textbox
                  const newProgress = { 
                    verbRoot: false,
                    negativeAffix: false,
                    tenseAffix: false,
                    personalAffix: false,
                    fullSentence: false
                  };
                  setProgress(newProgress);
                  setUserInput('');
                }
                // Don't notify parent - this is not manual input
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
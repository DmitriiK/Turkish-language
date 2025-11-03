import React, { useState, useEffect, useRef } from 'react';
import { Check, Target, BookOpen } from 'lucide-react';
import { TrainingExample, LearnDirection, ProgressState, LANGUAGE_LEVELS, LanguageLevel } from '@/types';
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

interface LearningCardProps {
};

// Helper function to format grammar name with level
const formatGrammarNameWithLevel = (tense: string, level: string | null): string => {
  const formattedName = formatGrammarName(tense);
  return level ? `${formattedName} (${level})` : formattedName;
};

interface LearningCardProps {
  example: TrainingExample;
  direction: LearnDirection;
  onProgress: (progress: ProgressState, wasManualInput?: boolean) => void;
  // Navigation props
  currentVerb: string;
  currentVerbDisplay: string;
  currentTense: string;
  currentPronoun: string | null;
  currentPolarity: 'positive' | 'negative';
  currentRank: number;
  languageLevel?: string; // Optional language level filter
  correctAnswers: number; // Correct answers counter
  isAnswered: boolean; // Whether this example has been answered correctly
  trackAnsweredCards: boolean; // Whether to track answered cards
  onTrackingChange: (enabled: boolean) => void; // Handler for tracking toggle
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
  // Navigation props
  currentVerb,
  currentVerbDisplay,
  currentTense,
  currentPronoun,
  currentPolarity,
  currentRank,
  languageLevel,
  correctAnswers,
  isAnswered,
  trackAnsweredCards,
  onTrackingChange,
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
  const [inputState, setInputState] = useState<'neutral' | 'correct' | 'error'>('neutral');
  const [tenseLevel, setTenseLevel] = useState<string | null>(null);
  const editableRef = useRef<HTMLDivElement>(null);

  // Load tense level mapping when component mounts or tense changes
  useEffect(() => {
    const loadTenseLevel = async () => {
      try {
        const base = (import.meta as any).env?.BASE_URL || '/';
        const response = await fetch(`${base}data/tense_level_mapping.json`);
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
    setInputState('neutral');
  }, [example]);

  // Handle direction changes - update input based on Reveal Answer state
  useEffect(() => {
    if (progress.fullSentence) {
      // If Reveal Answer is checked, show the appropriate translation
      setUserInput(buildTextFromProgress(progress));
    } else {
      // If Reveal Answer is not checked, clear the textbox
      setUserInput('');
    }
    // Reset input state to neutral on direction change
    setInputState('neutral');
  }, [direction]);

  // Get current cursor position in the contenteditable div
  const getCursorPosition = (): number => {
    if (!editableRef.current) return 0;
    
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return 0;
    
    const range = selection.getRangeAt(0);
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(editableRef.current);
    preCaretRange.setEnd(range.endContainer, range.endOffset);
    return preCaretRange.toString().length;
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
    
    if (!direction.endsWith('turkish')) {
      // For non-Turkish, just return plain text
      return userInput || '';
    }

    if (!userInput) {
      return '';
    }

    const targetSentence = getTargetSentence().replace(/\.+$/, ''); // Remove trailing dots
    const verbFull = example.turkish_verb.verb_full;
    const inputLower = userInput.toLowerCase();
    const verbIndex = inputLower.indexOf(verbFull.toLowerCase());
    const cursorPos = getCursorPosition();
    
    // Helper to check if a word sequence is incorrect
    const markIncorrectWords = (text: string, cursorPosition?: number) => {
      // Split both into words (preserve spaces)
      const words = text.split(/(\s+)/); // Keeps spaces as separate elements
      const targetWords = targetSentence.split(/(\s+)/).filter(w => !/^\s+$/.test(w)); // Get only non-space words from target
      
      // Find which word index contains the cursor
      let cursorWordIndex = -1;
      if (cursorPosition !== undefined) {
        let charCount = 0;
        for (let i = 0; i < words.length; i++) {
          charCount += words[i].length;
          if (cursorPosition <= charCount) {
            cursorWordIndex = i;
            break;
          }
        }
      }
      
      let html = '';
      
      for (let i = 0; i < words.length; i++) {
        const word = words[i];
        const isLastWord = i === words.length - 1;
        const isCursorWord = i === cursorWordIndex;
        const isSpace = /^\s+$/.test(word);
        
        // Check if word is definitely incorrect
        let isIncorrect = false;
        
        if (!isSpace) {
          // Remove trailing dots for comparison (user can type dots at the end)
          const wordWithoutDots = word.replace(/\.+$/, '');
          const wordLower = wordWithoutDots.toLowerCase();
          
          // If the word is just dots, don't mark as incorrect
          if (wordWithoutDots === '') {
            isIncorrect = false;
          } else {
            // Check if this word exists anywhere in the target sentence
            const existsInTarget = targetWords.some(tw => tw.toLowerCase() === wordLower);
            
            if (isLastWord || isCursorWord) {
              // Last word or word at cursor: check if it's a valid prefix of ANY word in target
              const isValidPrefix = targetWords.some(tw => tw.toLowerCase().startsWith(wordLower));
              isIncorrect = !isValidPrefix;
            } else {
              // Not last word and not at cursor: must exist exactly in target
              isIncorrect = !existsInTarget;
            }
          }
        }
        
        if (isIncorrect) {
          html += `<span style="text-decoration: underline; text-decoration-color: red; text-decoration-thickness: 2px;">${escapeHtml(word)}</span>`;
        } else {
          html += escapeHtml(word);
        }
      }
      
      return html;
    };
    
    // Helper to render text with incorrect parts marked in red
    const renderTextWithErrors = (beforeVerb: string, verbHtml: string, afterVerb: string, verbStartPos: number) => {
      let html = '';
      
      // Calculate cursor position relative to before/after sections
      const verbLength = userInput.length - beforeVerb.length - afterVerb.length;
      const verbEndPos = verbStartPos + verbLength;
      
      // Determine cursor position for each section
      let beforeCursorPos: number | undefined = undefined;
      let afterCursorPos: number | undefined = undefined;
      
      if (cursorPos <= verbStartPos) {
        // Cursor is in the "before" section
        beforeCursorPos = cursorPos;
      } else if (cursorPos > verbEndPos) {
        // Cursor is in the "after" section
        afterCursorPos = cursorPos - verbEndPos;
      }
      // If cursor is within the verb itself, we don't pass it to either section
      
      // Check text before verb word by word
      html += markIncorrectWords(beforeVerb, beforeCursorPos);
      
      // Add colored verb
      html += verbHtml;
      
      // Check text after verb word by word
      html += markIncorrectWords(afterVerb, afterCursorPos);
      
      return html;
    };
    
    if (verbIndex !== -1) {
      // Verb found in sentence - color it and check for errors
      let verbHtml = '';
      let verbOffset = verbIndex;
      
      if (example.turkish_verb.root) {
        verbHtml += `<span style="color: #1d4ed8; font-weight: bold;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.root.length))}</span>`;
        verbOffset += example.turkish_verb.root.length;
      }
      
      if (example.turkish_verb.negative_affix) {
        verbHtml += `<span style="color: #7e22ce;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.negative_affix.length))}</span>`;
        verbOffset += example.turkish_verb.negative_affix.length;
      }
      
      if (example.turkish_verb.tense_affix) {
        verbHtml += `<span style="color: #c2410c;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.tense_affix.length))}</span>`;
        verbOffset += example.turkish_verb.tense_affix.length;
      }
      
      if (example.turkish_verb.personal_affix) {
        verbHtml += `<span style="color: #15803d;">${escapeHtml(userInput.substring(verbOffset, verbOffset + example.turkish_verb.personal_affix.length))}</span>`;
        verbOffset += example.turkish_verb.personal_affix.length;
      }
      
      return renderTextWithErrors(
        userInput.substring(0, verbIndex),
        verbHtml,
        userInput.substring(verbIndex + verbFull.length),
        verbIndex
      );
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
        let verbHtml = '';
        let currentIndex = rootIndex;
        let verbEndIndex = rootIndex;
        
        // Try to match each part sequentially and build colored verb HTML
        for (const part of verbParts) {
          const partLower = part.text.toLowerCase();
          const remainingInput = userInput.substring(currentIndex).toLowerCase();
          
          if (remainingInput.startsWith(partLower)) {
            // This part matches - color it
            const actualText = userInput.substring(currentIndex, currentIndex + part.text.length);
            const style = part.bold 
              ? `color: ${part.color}; font-weight: bold;`
              : `color: ${part.color};`;
            verbHtml += `<span style="${style}">${escapeHtml(actualText)}</span>`;
            currentIndex += part.text.length;
            verbEndIndex = currentIndex;
          } else {
            // Part doesn't match - stop trying to match further parts
            break;
          }
        }
        
        // Calculate verb length for error checking
        return renderTextWithErrors(
          userInput.substring(0, rootIndex),
          verbHtml,
          userInput.substring(verbEndIndex),
          rootIndex
        );
      }
    }
    
    // No verb match found - check entire text for errors word by word
    return markIncorrectWords(userInput);
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

  // Determine grammar page URL based on direction
  const getGrammarPageUrl = () => {
    const lang = direction.startsWith('russian') ? 'ru' : 'en';
    return `/grammar/grammar-${lang}.html?tense=${example.turkish_verb.verb_tense}`;
  };

  // Get tooltip text based on language
  const getGrammarTooltip = () => {
    if (direction.startsWith('russian')) {
      return 'Открыть справочник по грамматике в новом окне';
    }
    return 'Open grammar reference in a new window';
  };

  // Render source sentence with colored Turkish verb when direction is from Turkish
  const renderSourceSentence = () => {
    if (!direction.startsWith('turkish')) {
      // Not learning from Turkish, return plain text
      return source.sentence;
    }

    // Learning from Turkish - color the verb parts in the Turkish sentence
    const sentence = example.turkish_example_sentence;
    const sentenceLower = sentence.toLowerCase();
    
    // Try to find the verb in the sentence
    // First try: look for verb_full
    let verbIndex = sentenceLower.indexOf(example.turkish_verb.verb_full.toLowerCase());
    let verbLength = example.turkish_verb.verb_full.length;
    
    // Second try: build verb from components
    if (verbIndex === -1) {
      let verbToFind = '';
      if (example.turkish_verb.root) verbToFind += example.turkish_verb.root;
      if (example.turkish_verb.negative_affix) verbToFind += example.turkish_verb.negative_affix;
      if (example.turkish_verb.tense_affix) verbToFind += example.turkish_verb.tense_affix;
      if (example.turkish_verb.personal_affix) verbToFind += example.turkish_verb.personal_affix;
      
      verbIndex = sentenceLower.indexOf(verbToFind.toLowerCase());
      verbLength = verbToFind.length;
    }

    if (verbIndex === -1) {
      // Verb not found at all - this is a data issue, just return plain text
      return sentence;
    }

    // Build colored verb JSX
    const beforeVerb = sentence.substring(0, verbIndex);
    const afterVerb = sentence.substring(verbIndex + verbLength);
    
    let verbOffset = 0;
    const verbParts: JSX.Element[] = [];

    // Root (blue, bold)
    if (example.turkish_verb.root) {
      const rootText = sentence.substring(verbIndex + verbOffset, verbIndex + verbOffset + example.turkish_verb.root.length);
      verbParts.push(
        <span key="root" className="text-blue-600 font-bold">
          {rootText}
        </span>
      );
      verbOffset += example.turkish_verb.root.length;
    }

    // Negative affix (purple)
    if (example.turkish_verb.negative_affix) {
      const negText = sentence.substring(verbIndex + verbOffset, verbIndex + verbOffset + example.turkish_verb.negative_affix.length);
      verbParts.push(
        <span key="negative" className="text-purple-600">
          {negText}
        </span>
      );
      verbOffset += example.turkish_verb.negative_affix.length;
    }

    // Tense affix (orange) - may include vowel harmony connector
    if (example.turkish_verb.tense_affix) {
      const tenseText = sentence.substring(verbIndex + verbOffset, verbIndex + verbOffset + example.turkish_verb.tense_affix.length);
      verbParts.push(
        <span key="tense" className="text-orange-700">
          {tenseText}
        </span>
      );
      verbOffset += example.turkish_verb.tense_affix.length;
    }

    // Check if there's a vowel harmony connector before personal affix
    // This handles cases where verb parts don't add up to verb_full length
    const remainingLength = verbLength - verbOffset;
    const personalAffixLength = example.turkish_verb.personal_affix?.length || 0;
    
    // Personal affix (green) - includes any vowel harmony connector
    if (example.turkish_verb.personal_affix) {
      // If there's extra characters (vowel harmony), include them with personal affix
      const actualPersonalLength = Math.max(personalAffixLength, remainingLength);
      const personalText = sentence.substring(verbIndex + verbOffset, verbIndex + verbOffset + actualPersonalLength);
      verbParts.push(
        <span key="personal" className="text-green-700">
          {personalText}
        </span>
      );
      verbOffset += actualPersonalLength;
    }
    
    return (
      <>
        {beforeVerb}
        {verbParts}
        {afterVerb}
      </>
    );
  };

  return (
    <div className="card max-w-full mx-auto animate-fade-in">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="text-lg text-gray-600 flex items-center gap-2 font-medium">
              <span>#{example.verb_rank} •</span>
              <div className="relative group">
                <a
                  href={getGrammarPageUrl()}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors"
                >
                  {formatGrammarNameWithLevel(example.turkish_verb.verb_tense, tenseLevel)}
                </a>
                {/* Custom tooltip with 2x bigger text */}
                <div className="invisible group-hover:visible absolute left-0 top-full mt-2 px-3 py-2 bg-gray-900 text-white text-base rounded-lg shadow-lg z-50 whitespace-nowrap pointer-events-none">
                  {getGrammarTooltip()}
                  <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
                </div>
              </div>
            </div>
            {/* Language Level Selector */}
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-primary-600" />
              <select
                value={languageLevel || 'All'}
                onChange={(e) => onLevelChange(e.target.value as LanguageLevel)}
                className="px-3 py-1 border border-gray-300 rounded text-base focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {LANGUAGE_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="text-lg font-semibold text-primary-600">
            {source.language} → {targetLanguage}
          </div>
        </div>
        
        <div className={clsx(
          "text-center mb-10 p-10 rounded-lg transition-colors min-h-[200px] flex flex-col justify-center",
          isAnswered ? "bg-green-50" : "bg-gray-50"
        )}>
          <div className="text-3xl font-semibold text-gray-700 mb-6">
            {source.verb}
          </div>
          <div className="text-4xl text-gray-900 leading-relaxed">
            <span>"</span>
            {renderSourceSentence()}
            <span>"</span>
          </div>
        </div>
      </div>

      {/* Main Input Section */}
      <div className="mb-10">
        <label className="block text-2xl font-semibold text-gray-700 mb-6">
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
            className={clsx(
              'input text-3xl min-h-[6rem] outline-none py-6',
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
      </div>

      {/* Progress Section */}
      <div className="mt-8">
        {/* Status and Counter */}
        <div className="flex items-center justify-between mb-6">
          <span
            className={clsx(
              'text-lg font-bold',
              isAnswered 
                ? 'text-green-600'
                : 'text-gray-500'
            )}
          >
            {isAnswered ? 'Answered' : 'Not Answered'}
          </span>
          
          {/* Track Answered Cards Checkbox */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="track-answered"
              checked={trackAnsweredCards}
              onChange={(e) => onTrackingChange(e.target.checked)}
              className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-2 focus:ring-primary-500 cursor-pointer"
            />
            <label 
              htmlFor="track-answered" 
              className="text-base text-gray-700 cursor-pointer select-none font-medium"
              title="Track which cards you've answered correctly"
            >
              Track Progress on your local machine
            </label>
          </div>

          {/* Correct Answers Counter */}
          <div 
            className="bg-green-50 border-2 border-green-500 rounded-lg px-4 py-2"
            title="Unique examples completed"
          >
            <div className="flex items-center gap-2">
              <Target className="w-6 h-6 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {correctAnswers}
              </span>
            </div>
          </div>
        </div>

        {/* Progress Checkboxes */}
        <div className="flex flex-wrap gap-4">
          <ProgressCheckbox
            label="Verb Root"
            checked={progress.verbRoot}
            color="blue"
            onToggle={() => {
              const newProgress = { ...progress, verbRoot: !progress.verbRoot };
              setProgress(newProgress);
              if (isLearningTurkish) {
                setUserInput(buildTextFromProgress(newProgress));
              }
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
                if (isLearningTurkish) {
                  setUserInput(buildTextFromProgress(newProgress));
                }
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
              if (isLearningTurkish) {
                setUserInput(buildTextFromProgress(newProgress));
              }
            }}
          />
          <ProgressCheckbox
            label="Personal Affix"
            checked={progress.personalAffix}
            color="green"
            onToggle={() => {
              const newProgress = { ...progress, personalAffix: !progress.personalAffix };
              setProgress(newProgress);
              if (isLearningTurkish) {
                setUserInput(buildTextFromProgress(newProgress));
              }
            }}
          />
          <ProgressCheckbox
            label="Reveal Answer"
            checked={progress.fullSentence}
            color="gray"
            onToggle={() => {
              const isChecking = !progress.fullSentence;
              
              if (isChecking) {
                // If checking Reveal Answer, check all components too
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
                // If unchecking Reveal Answer, uncheck all components and clear textbox
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
            }}
          />
        </div>
      </div>

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
    <div className="flex items-center gap-3">
      <div 
        className={clsx(
          'w-6 h-6 border-2 rounded flex items-center justify-center transition-colors cursor-pointer',
          checked 
            ? `${colors.bg} ${colors.border}`
            : `border-gray-300 ${colors.hover}`
        )}
        onClick={onToggle}
      >
        {checked && (
          <Check className="w-4 h-4 text-white" />
        )}
      </div>
      <span 
        className={clsx(
          'text-base font-medium cursor-pointer transition-colors',
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
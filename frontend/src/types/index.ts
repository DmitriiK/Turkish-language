// Core Turkish language learning types based on the existing data structure

export interface TurkishVerb {
  verb_full: string;
  root: string;
  tense_affix: string;
  verb_tense: string;
  personal_pronoun: string | null;
  personal_affix: string | null;
  polarity: 'positive' | 'negative';
  negative_affix: string | null;
}

export interface TrainingExample {
  verb_rank: number;
  verb_english: string;
  verb_russian: string;
  verb_infinitive: string;
  turkish_verb: TurkishVerb;
  english_example_sentence: string;
  russian_example_sentence: string;
  turkish_example_sentence: string;
  turkish_example_sentence_with_blank: string;
}

export type LearnDirection = 
  | 'english-to-turkish'
  | 'russian-to-turkish' 
  | 'turkish-to-english'
  | 'turkish-to-russian';

export interface LearningSession {
  direction: LearnDirection;
  currentExample: TrainingExample;
  verbRank: number;
  tenseIndex: number;
  pronounIndex: number;
}

export interface ProgressState {
  verbRoot: boolean;
  negativeAffix: boolean;
  tenseAffix: boolean;
  personalAffix: boolean;
  fullSentence: boolean;
}

export interface NavigationIndex {
  verbs: string[];
  tenses: Record<string, string[]>; // verb -> tenses available
  pronouns: Record<string, Record<string, string[]>>; // verb -> tense -> pronouns
}

export interface UserProgress {
  correctAnswers: number;
  totalAttempts: number;
  currentStreak: number;
  bestStreak: number;
  completedExamples: Set<string>; // Track unique completed examples
}

// Available language levels
export const LANGUAGE_LEVELS = ['All', 'A1', 'A2', 'B1', 'B2', 'A1-A2', 'B1-B2'] as const;
export type LanguageLevel = typeof LANGUAGE_LEVELS[number];

// Available pronouns
export const PRONOUNS = ['ben', 'sen', 'o', 'biz', 'siz', 'onlar'] as const;
export type Pronoun = typeof PRONOUNS[number];

// Learning directions with display names
export const LEARNING_DIRECTIONS: Record<LearnDirection, string> = {
  'english-to-turkish': 'English → Turkish',
  'russian-to-turkish': 'Russian → Turkish', 
  'turkish-to-english': 'Turkish → English',
  'turkish-to-russian': 'Turkish → Russian'
};

// Language level filtering
export interface LevelFilter {
  selectedLevel: LanguageLevel;
}

// Navigation tooltip data
export interface TooltipData {
  verb?: string;
  tense?: string;
  pronoun?: string;
}
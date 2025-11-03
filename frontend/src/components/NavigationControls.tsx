import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, ChevronDown, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { dataLoader } from '@/utils/dataLoader';

interface NavigationControlsProps {
  currentVerb: string; // Internal English verb name (e.g., "be")
  currentVerbDisplay: string; // Display label (English or Turkish based on direction)
  currentTense: string;
  currentPronoun: string | null;
  currentPolarity: 'positive' | 'negative';
  currentRank: number;
  languageLevel?: string; // Optional language level filter
  direction: 'english-to-turkish' | 'russian-to-turkish' | 'turkish-to-english' | 'turkish-to-russian';
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

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  currentVerb,
  currentVerbDisplay,
  currentTense,
  currentPronoun,
  currentPolarity,
  currentRank,
  languageLevel,
  direction,
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
  const [currentTenseLevel, setCurrentTenseLevel] = React.useState<string>('');

  // Load the language level for the current tense
  React.useEffect(() => {
    const loadTenseLevel = async () => {
      try {
        const tenseLevelMapping = await dataLoader.loadTenseLevelMapping();
        const level = tenseLevelMapping[currentTense] || '';
        setCurrentTenseLevel(level);
      } catch (error) {
        console.error('Error loading tense level:', error);
      }
    };
    loadTenseLevel();
  }, [currentTense]);

  // Enhanced navigation handlers with circular wrapping
  // Navigate by rank (1, 2, 3...) instead of array position
  const handlePrevVerbWithWrap = async () => {
    const verbsWithRanks = await dataLoader.getVerbsWithRanks();
    const totalVerbs = verbsWithRanks.length;
    
    // Find previous rank (circular)
    const prevRank = currentRank > 1 ? currentRank - 1 : totalVerbs;
    const prevVerbData = verbsWithRanks.find(v => v.rank === prevRank);
    
    if (prevVerbData) {
      onGoToVerb(prevVerbData.verb);
    }
  };

  const handleNextVerbWithWrap = async () => {
    const verbsWithRanks = await dataLoader.getVerbsWithRanks();
    const totalVerbs = verbsWithRanks.length;
    
    // Find next rank (circular)
    const nextRank = currentRank < totalVerbs ? currentRank + 1 : 1;
    const nextVerbData = verbsWithRanks.find(v => v.rank === nextRank);
    
    if (nextVerbData) {
      onGoToVerb(nextVerbData.verb);
    }
  };

  const handlePrevTenseWithWrap = async () => {
    const prevTense = await dataLoader.getPrevTense(currentVerb, currentTense, languageLevel);
    if (prevTense) {
      onPrevTense();
    } else {
      // Wrap to last tense
      const allTenses = await dataLoader.getAvailableTenses(currentVerb, languageLevel);
      const lastTense = allTenses[allTenses.length - 1];
      if (lastTense && lastTense !== currentTense) {
        onGoToTense(lastTense);
      }
    }
  };

  const handleNextTenseWithWrap = async () => {
    const nextTense = await dataLoader.getNextTense(currentVerb, currentTense, languageLevel);
    if (nextTense) {
      onNextTense();
    } else {
      // Wrap to first tense
      const allTenses = await dataLoader.getAvailableTenses(currentVerb, languageLevel);
      const firstTense = allTenses[0];
      if (firstTense && firstTense !== currentTense) {
        onGoToTense(firstTense);
      }
    }
  };

  const handlePrevPronounWithWrap = async () => {
    const prevPronoun = await dataLoader.getPrevPronoun(currentVerb, currentTense, currentPronoun || '');
    if (prevPronoun) {
      onPrevPronoun();
    } else {
      // Wrap to last pronoun
      const allPronouns = await dataLoader.getAvailablePronouns(currentVerb, currentTense);
      const lastPronoun = allPronouns[allPronouns.length - 1];
      if (lastPronoun && lastPronoun !== currentPronoun) {
        onGoToPronoun(lastPronoun);
      }
    }
  };

  const handleNextPronounWithWrap = async () => {
    const nextPronoun = await dataLoader.getNextPronoun(currentVerb, currentTense, currentPronoun || '');
    if (nextPronoun) {
      onNextPronoun();
    } else {
      // Wrap to first pronoun
      const allPronouns = await dataLoader.getAvailablePronouns(currentVerb, currentTense);
      const firstPronoun = allPronouns[0];
      if (firstPronoun && firstPronoun !== currentPronoun) {
        onGoToPronoun(firstPronoun);
      }
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-base font-medium text-gray-700 mb-4">Navigation</h3>
      
      {/* Current Position */}
      <div className="mb-5 p-4 bg-gray-50 rounded text-sm">
        <span className="font-medium">Current:</span> {currentVerb} (#{currentRank}) • {currentTense.replace('_', ' ')}
        {currentPronoun && <> • {currentPronoun}</>} • {currentPolarity}
      </div>

      {/* Unified Navigation Row */}
      <div className="grid grid-cols-4 gap-2">
        {/* Verb Navigation Control with Rank */}
        <div>
          <div className="text-base font-semibold text-gray-600 mb-1 px-1">
            {direction === 'turkish-to-english' || direction === 'turkish-to-russian' ? 'Fiil Seç' : direction === 'russian-to-turkish' ? 'Выбрать глагол' : 'Choose Verb'}
          </div>
          <NavigationTriple
            label={`${currentRank}. ${currentVerbDisplay}`}
            onPrev={handlePrevVerbWithWrap}
            onNext={handleNextVerbWithWrap}
            onCenter={() => {}}
            dropdownItems={[]} // Will be populated by NavigationTriple component
            searchable={true}
            loadDropdownItems={async () => {
              const verbsWithRank = await dataLoader.getVerbsWithRanks();
              const isTurkishSource = direction === 'turkish-to-english' || direction === 'turkish-to-russian';
              
              return verbsWithRank.map(({ verb, rank, turkishInfinitive }) => ({
                label: isTurkishSource ? `${rank}. ${turkishInfinitive}` : `${rank}. ${verb}`,
                value: verb, // Always use English as the internal value
                onSelect: () => onGoToVerb(verb)
              }));
            }}
          />
        </div>

        {/* Tense Navigation Control */}
        <div>
          <div className="text-base font-semibold text-gray-600 mb-1 px-1">
            {direction === 'turkish-to-english' || direction === 'turkish-to-russian' ? 'Gramer Formu' : direction === 'russian-to-turkish' ? 'Грамматическая форма' : 'Grammar Form'}
          </div>
          <NavigationTriple
            label={currentTenseLevel ? `${currentTenseLevel}: ${currentTense.replace(/_/g, ' ')}` : currentTense.replace(/_/g, ' ')}
            onPrev={handlePrevTenseWithWrap}
            onNext={handleNextTenseWithWrap}
            onCenter={() => {}}
            dropdownItems={[]} // Will be populated by NavigationTriple component
            searchable={false}
            loadDropdownItems={async () => {
              const tenses = await dataLoader.getAvailableTenses(currentVerb, languageLevel);
              
              // Get language level for each tense and create items
              const tenseLevelMapping = await dataLoader.loadTenseLevelMapping();
              const tenseItems = tenses.map(tense => {
                const level = tenseLevelMapping[tense] || '??';
                return {
                  tense,
                  level,
                  label: `${level}: ${tense.replace(/_/g, ' ')}`,
                  value: tense,
                  onSelect: () => onGoToTense(tense)
                };
              });
              
              // Sort by language level (A1, A2, B1, B2, C1, C2) then by tense name
              const levelOrder: { [key: string]: number } = {
                'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6
              };
              
              return tenseItems.sort((a, b) => {
                const levelDiff = (levelOrder[a.level] || 99) - (levelOrder[b.level] || 99);
                if (levelDiff !== 0) return levelDiff;
                return a.tense.localeCompare(b.tense);
              });
            }}
          />
        </div>

        {/* Pronoun Navigation Control */}
        <div>
          <div className="text-base font-semibold text-gray-600 mb-1 px-1">
            {direction === 'turkish-to-english' || direction === 'turkish-to-russian' ? 'Zamir' : direction === 'russian-to-turkish' ? 'Местоимение' : 'Pronoun'}
          </div>
          <NavigationTriple
            label={currentPronoun || 'none'}
            onPrev={handlePrevPronounWithWrap}
            onNext={handleNextPronounWithWrap}
            onCenter={() => {}}
            dropdownItems={[]} // Will be populated by NavigationTriple component
            searchable={false}
            loadDropdownItems={async () => {
              const pronouns = await dataLoader.getAvailablePronouns(currentVerb, currentTense, currentPolarity);
              return pronouns.map(pronoun => ({
                label: pronoun,
                value: pronoun,
                onSelect: () => onGoToPronoun(pronoun)
              }));
            }}
          />
        </div>

        {/* Polarity Navigation Control */}
        <div>
          <div className="text-base font-semibold text-gray-600 mb-1 px-1">
            {direction === 'turkish-to-english' || direction === 'turkish-to-russian' ? 'Olumlu/Olumsuz' : direction === 'russian-to-turkish' ? 'Положительное/Отрицательное' : 'Positive/Negative'}
          </div>
          <NavigationTriple
            label={currentPolarity === 'positive' ? '✓ positive' : '✗ negative'}
            onPrev={onPrevPolarity}
            onNext={onNextPolarity}
            onCenter={() => {}}
            dropdownItems={[
              {
                label: '✓ positive',
                value: 'positive',
                onSelect: () => onGoToPolarity('positive')
              },
              {
                label: '✗ negative',
                value: 'negative',
                onSelect: () => onGoToPolarity('negative')
              }
            ]}
            searchable={false}
          />
        </div>
      </div>
    </div>
  );
};

interface DropdownItem {
  label: string;
  value: string;
  onSelect: () => void;
}
interface DropdownItem {
  label: string;
  value: string;
  onSelect: () => void;
}

interface NavigationTripleProps {
  label: string;
  onPrev: () => void;
  onNext: () => void;
  onCenter: () => void;
  dropdownItems: DropdownItem[];
  searchable?: boolean;
  loadDropdownItems?: () => Promise<DropdownItem[]>;
}

const NavigationTriple: React.FC<NavigationTripleProps> = ({
  label,
  onPrev,
  onNext,
  onCenter,
  dropdownItems: initialDropdownItems,
  searchable = false,
  loadDropdownItems
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownItems, setDropdownItems] = useState<DropdownItem[]>(initialDropdownItems);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && loadDropdownItems) {
      setLoading(true);
      loadDropdownItems().then(items => {
        setDropdownItems(items);
        setLoading(false);
      });
    }
  }, [isOpen, loadDropdownItems]);

  const filteredItems = searchable 
    ? dropdownItems.filter(item => 
        item.label.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : dropdownItems;

  const handleCenterClick = () => {
    setIsOpen(!isOpen);
    onCenter();
  };

  const handleItemSelect = (item: DropdownItem) => {
    item.onSelect();
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative">
      <div className="flex border border-gray-300 rounded-lg overflow-hidden">
        {/* Left Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onPrev}
          className="px-3 py-2 bg-primary-50 border-r border-gray-300 hover:bg-primary-100 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-primary-600" />
        </motion.button>

        {/* Center Button */}
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={handleCenterClick}
          className="px-4 py-2 bg-white hover:bg-gray-50 flex-1 text-base font-medium text-gray-700 flex items-center justify-center gap-2 min-w-0"
        >
          <span className="truncate">{label}</span>
          <ChevronDown className={clsx("w-4 h-4 transition-transform", isOpen && "rotate-180")} />
        </motion.button>

        {/* Right Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onNext}
          className="px-3 py-2 bg-primary-50 border-l border-gray-300 hover:bg-primary-100 transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-primary-600" />
        </motion.button>
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 z-10 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-hidden"
          >
            {searchable && (
              <div className="p-2 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9 pr-3 py-2 w-full text-base border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>
            )}
            
            <div className="overflow-y-auto max-h-48">
              {loading ? (
                <div className="p-4 text-center text-base text-gray-500">Loading...</div>
              ) : filteredItems.length === 0 ? (
                <div className="p-4 text-center text-base text-gray-500">No items found</div>
              ) : (
                filteredItems.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => handleItemSelect(item)}
                    className="w-full px-4 py-2.5 text-left text-base hover:bg-primary-50 hover:text-primary-600 transition-colors"
                  >
                    {item.label}
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
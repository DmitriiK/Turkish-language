import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, ChevronDown, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import { dataLoader } from '@/utils/dataLoader';

interface NavigationControlsProps {
  currentVerb: string;
  currentTense: string;
  currentPronoun: string | null;
  currentPolarity: 'positive' | 'negative';
  currentRank: number;
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
  currentTense,
  currentPronoun,
  currentPolarity,
  currentRank,
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
    const prevTense = await dataLoader.getPrevTense(currentVerb, currentTense);
    if (prevTense) {
      onPrevTense();
    } else {
      // Wrap to last tense
      const allTenses = await dataLoader.getAvailableTenses(currentVerb);
      const lastTense = allTenses[allTenses.length - 1];
      if (lastTense && lastTense !== currentTense) {
        onGoToTense(lastTense);
      }
    }
  };

  const handleNextTenseWithWrap = async () => {
    const nextTense = await dataLoader.getNextTense(currentVerb, currentTense);
    if (nextTense) {
      onNextTense();
    } else {
      // Wrap to first tense
      const allTenses = await dataLoader.getAvailableTenses(currentVerb);
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
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Navigation</h3>
      
      {/* Current Position */}
      <div className="mb-4 p-3 bg-gray-50 rounded text-xs">
        <span className="font-medium">Current:</span> {currentVerb} (#{currentRank}) • {currentTense.replace('_', ' ')}
        {currentPronoun && <> • {currentPronoun}</>} • {currentPolarity}
      </div>

      {/* Unified Navigation Row */}
      <div className="grid grid-cols-4 gap-2">
        {/* Verb Navigation Control with Rank */}
        <NavigationTriple
          label={`${currentRank}. ${currentVerb.replace('to ', '')}`}
          onPrev={handlePrevVerbWithWrap}
          onNext={handleNextVerbWithWrap}
          onCenter={() => {}}
          dropdownItems={[]} // Will be populated by NavigationTriple component
          searchable={true}
          loadDropdownItems={async () => {
            const verbsWithRank = await dataLoader.getVerbsWithRanks();
            return verbsWithRank.map(({ verb, rank }) => ({
              label: `${rank}. ${verb}`,
              value: verb,
              onSelect: () => onGoToVerb(verb)
            }));
          }}
        />

        {/* Tense Navigation Control */}
        <NavigationTriple
          label={currentTense.replace('_', ' ')}
          onPrev={handlePrevTenseWithWrap}
          onNext={handleNextTenseWithWrap}
          onCenter={() => {}}
          dropdownItems={[]} // Will be populated by NavigationTriple component
          searchable={false}
          loadDropdownItems={async () => {
            const tenses = await dataLoader.getAvailableTenses(currentVerb);
            return tenses.map(tense => ({
              label: tense.replace('_', ' '),
              value: tense,
              onSelect: () => onGoToTense(tense)
            }));
          }}
        />

        {/* Pronoun Navigation Control */}
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

        {/* Polarity Navigation Control */}
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
    if (isOpen && loadDropdownItems && dropdownItems.length === 0) {
      setLoading(true);
      loadDropdownItems().then(items => {
        setDropdownItems(items);
        setLoading(false);
      });
    }
  }, [isOpen, loadDropdownItems, dropdownItems.length]);

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
          className="px-2 py-1 bg-primary-50 border-r border-gray-300 hover:bg-primary-100 transition-colors"
        >
          <ChevronLeft className="w-4 h-4 text-primary-600" />
        </motion.button>

        {/* Center Button */}
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={handleCenterClick}
          className="px-3 py-1 bg-white hover:bg-gray-50 flex-1 text-sm font-medium text-gray-700 flex items-center justify-center gap-1 min-w-0"
        >
          <span className="truncate">{label}</span>
          <ChevronDown className={clsx("w-3 h-3 transition-transform", isOpen && "rotate-180")} />
        </motion.button>

        {/* Right Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onNext}
          className="px-2 py-1 bg-primary-50 border-l border-gray-300 hover:bg-primary-100 transition-colors"
        >
          <ChevronRight className="w-4 h-4 text-primary-600" />
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
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8 pr-2 py-1 w-full text-sm border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>
            )}
            
            <div className="overflow-y-auto max-h-48">
              {loading ? (
                <div className="p-3 text-center text-sm text-gray-500">Loading...</div>
              ) : filteredItems.length === 0 ? (
                <div className="p-3 text-center text-sm text-gray-500">No items found</div>
              ) : (
                filteredItems.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => handleItemSelect(item)}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-primary-50 hover:text-primary-600 transition-colors"
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
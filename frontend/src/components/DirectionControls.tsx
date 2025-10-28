import React from 'react';
import { Globe, BookOpen, ArrowLeftRight } from 'lucide-react';
import { LearnDirection, LanguageLevel, LANGUAGE_LEVELS } from '@/types';

interface DirectionControlsProps {
  currentDirection: LearnDirection;
  onDirectionChange: (direction: LearnDirection) => void;
  currentLevel: LanguageLevel;
  onLevelChange: (level: LanguageLevel) => void;
}

export const DirectionControls: React.FC<DirectionControlsProps> = ({
  currentDirection,
  onDirectionChange,
  currentLevel,
  onLevelChange
}) => {
  // Determine current source language
  const sourceLanguage = currentDirection.includes('english') ? 'english' : 'russian';
  const isToTurkish = currentDirection.includes('to-turkish');

  // Handle source language change
  const handleSourceLanguageChange = (newSource: 'english' | 'russian') => {
    const newDirection: LearnDirection = isToTurkish 
      ? `${newSource}-to-turkish` 
      : `turkish-to-${newSource}`;
    onDirectionChange(newDirection);
  };

  // Handle direction toggle
  const handleDirectionToggle = () => {
    const newDirection: LearnDirection = isToTurkish
      ? `turkish-to-${sourceLanguage}` as LearnDirection
      : `${sourceLanguage}-to-turkish` as LearnDirection;
    onDirectionChange(newDirection);
  };

  // Get direction button label
  const getDirectionLabel = () => {
    if (sourceLanguage === 'english') {
      return isToTurkish ? 'English → Turkish' : 'Türkçe → İngilizce';
    } else {
      return isToTurkish ? 'Русский → Турецкий' : 'Türkçe → Rusça';
    }
  };

  return (
    <div className="flex items-center gap-6 mb-4 flex-wrap">
      {/* Source Language Selector */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-primary-600" />
          <label className="text-sm font-medium text-gray-700">Source Language:</label>
        </div>
        <select
          value={sourceLanguage}
          onChange={(e) => handleSourceLanguageChange(e.target.value as 'english' | 'russian')}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="english">English</option>
          <option value="russian">Русский (Russian)</option>
        </select>
      </div>

      {/* Direction Toggle Button */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <ArrowLeftRight className="w-4 h-4 text-primary-600" />
          <label className="text-sm font-medium text-gray-700">Direction:</label>
        </div>
        <button
          onClick={handleDirectionToggle}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors flex items-center gap-2"
        >
          {getDirectionLabel()}
        </button>
      </div>

      {/* Language Level Selector */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-primary-600" />
          <label className="text-sm font-medium text-gray-700">Language Level:</label>
        </div>
        <select
          value={currentLevel}
          onChange={(e) => onLevelChange(e.target.value as LanguageLevel)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          {LANGUAGE_LEVELS.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

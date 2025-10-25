import React from 'react';
import { Globe, BookOpen } from 'lucide-react';
import { LearnDirection, LEARNING_DIRECTIONS, LanguageLevel, LANGUAGE_LEVELS } from '@/types';

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
  const directions = Object.entries(LEARNING_DIRECTIONS) as [LearnDirection, string][];

  return (
    <div className="flex items-center gap-6 mb-4 flex-wrap">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-primary-600" />
          <label className="text-sm font-medium text-gray-700">Learning Direction:</label>
        </div>
        <select
          value={currentDirection}
          onChange={(e) => onDirectionChange(e.target.value as LearnDirection)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          {directions.map(([direction, label]) => (
            <option key={direction} value={direction}>
              {label}
            </option>
          ))}
        </select>
      </div>

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


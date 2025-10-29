import React from 'react';
import { ArrowLeftRight } from 'lucide-react';
import { LearnDirection } from '@/types';

interface DirectionControlsProps {
  currentDirection: LearnDirection;
  onDirectionChange: (direction: LearnDirection) => void;
}

// Flag components
const TurkeyFlag = () => <span className="text-8xl">🇹🇷</span>;
const UKFlag = () => <span className="text-8xl">🇬🇧</span>;
const RussiaFlag = () => <span className="text-8xl">🇷🇺</span>;

export const DirectionControls: React.FC<DirectionControlsProps> = ({
  currentDirection,
  onDirectionChange
}) => {
  // Determine current source language
  const sourceLanguage = currentDirection.includes('english') ? 'english' : 'russian';
  const isToTurkish = currentDirection.includes('to-turkish');

  // Handle direction toggle (swap languages)
  const handleDirectionToggle = () => {
    const newDirection: LearnDirection = isToTurkish
      ? `turkish-to-${sourceLanguage}` as LearnDirection
      : `${sourceLanguage}-to-turkish` as LearnDirection;
    onDirectionChange(newDirection);
  };

  // Get the flags based on direction
  const getLeftFlag = () => {
    if (isToTurkish) {
      return sourceLanguage === 'english' ? <UKFlag /> : <RussiaFlag />;
    }
    return <TurkeyFlag />;
  };

  const getRightFlag = () => {
    if (isToTurkish) {
      return <TurkeyFlag />;
    }
    return sourceLanguage === 'english' ? <UKFlag /> : <RussiaFlag />;
  };

  return (
    <div className="space-y-4">
      {/* Flags with Swap Button */}
      <div className="flex items-start justify-center gap-6">
        {/* Left Flag */}
        <div className="flex flex-col items-center gap-2">
          {getLeftFlag()}
        </div>

        {/* Swap Button - Square and positioned higher */}
        <button
          onClick={handleDirectionToggle}
          className="p-3 border-2 border-primary-500 rounded-lg hover:bg-primary-50 focus:ring-2 focus:ring-primary-500 transition-all transform hover:scale-110 mt-4"
          title="Swap languages"
        >
          <ArrowLeftRight className="w-6 h-6 text-primary-600" />
        </button>

        {/* Right Flag */}
        <div className="flex flex-col items-center gap-2">
          {getRightFlag()}
        </div>
      </div>
    </div>
  );
};
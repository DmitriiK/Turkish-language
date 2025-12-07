# Frontend Model Display Implementation

## Overview

The frontend now displays the LLM model name that generated each training example on the verb card.

## Visual Design

### Location
The model badge appears in the card header, next to the grammar form name:

```
#4 • şimdiki zaman (A1)  [CLAUDE - anthropic.claude-3-5-sonnet-20241022-v2:0]  📚 All
```

### Styling
- **Badge**: Purple background (`bg-purple-100`) with purple text (`text-purple-700`)
- **Size**: Small text (`text-xs`) with padding
- **Shape**: Rounded corners (`rounded-md`)
- **Cursor**: Help cursor to indicate there's more information on hover

### Interactive Features
- **Hover Tooltip**: When you hover over the model badge, a tooltip appears showing the generation timestamp
- **Format**: "Generated: 12/6/2024, 3:30:45 PM" (localized to user's timezone)

## Code Changes

### 1. TypeScript Types (`frontend/src/types/index.ts`)

Added optional metadata fields to `TrainingExample` interface:

```typescript
export interface TrainingExample {
  // ... existing fields ...
  generated_by_model?: string; // Optional: LLM model that generated this example
  generated_at?: string; // Optional: ISO 8601 timestamp of generation
}
```

### 2. Learning Card Component (`frontend/src/components/LearningCard.tsx`)

Added model badge display in the card header:

```tsx
{/* Model name badge if available */}
{example.generated_by_model && (
  <div className="relative group/model">
    <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-md font-normal cursor-help">
      {example.generated_by_model}
    </span>
    {/* Tooltip showing generation date if available */}
    {example.generated_at && (
      <div className="invisible group-hover/model:visible absolute left-0 top-full mt-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg shadow-lg z-50 whitespace-nowrap pointer-events-none">
        Generated: {new Date(example.generated_at).toLocaleString()}
        <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
      </div>
    )}
  </div>
)}
```

## Behavior

### With Metadata
Examples that have the `generated_by_model` field will display:
1. The model badge in purple
2. Hovering shows generation timestamp (if available)

### Without Metadata (Backward Compatible)
Examples without the metadata field (older examples) will:
1. Display normally without the badge
2. Work exactly as before

## Example JSON

```json
{
  "verb_rank": 4,
  "verb_english": "say",
  "turkish_example_sentence": "Ben gizli planı hakkında hiçbir şey söylemiyorum",
  "generated_by_model": "CLAUDE - anthropic.claude-3-5-sonnet-20241022-v2:0",
  "generated_at": "2024-12-06T15:30:45.123456+00:00"
}
```

## Browser Compatibility

- **Tailwind CSS**: Uses standard Tailwind classes that work in all modern browsers
- **Group Hover**: The `group/model` syntax is for nested groups (Tailwind v3.2+)
- **Date Formatting**: Uses native `Date.toLocaleString()` which is supported in all modern browsers

## Future Enhancements

Possible improvements:
1. Filter examples by model
2. Show model statistics (accuracy, examples count)
3. Color-code different models
4. Add a legend explaining model names

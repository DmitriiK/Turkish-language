# Flags Directory

This directory is reserved for flag images if you want to use custom SVG or PNG files instead of emoji flags.

## Current Implementation
The app currently uses emoji flags (🇹🇷 🇬🇧 🇷🇺) which work across all platforms.

## To Use Custom Images
If you want to use custom flag images:

1. Add flag files here:
   - `turkey.svg` or `turkey.png`
   - `uk.svg` or `uk.png`
   - `russia.svg` or `russia.png`

2. Update the flag components in `/src/components/DirectionControls.tsx`:
   ```tsx
   const TurkeyFlag = () => <img src="/graphics/flags/turkey.svg" alt="Turkey" className="w-12 h-12" />;
   const UKFlag = () => <img src="/graphics/flags/uk.svg" alt="UK" className="w-12 h-12" />;
   const RussiaFlag = () => <img src="/graphics/flags/russia.svg" alt="Russia" className="w-12 h-12" />;
   ```

## Recommended Sources for Flag Images
- [Flagpedia](https://flagpedia.net/) - Free SVG flags
- [Country Flags](https://www.countryflags.com/) - Various formats
- [Flaticon](https://www.flaticon.com/free-icons/flag) - Icon packs

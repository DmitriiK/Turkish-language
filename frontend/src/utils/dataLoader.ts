import { TrainingExample } from '@/types';

// Main verbs index (lightweight)
interface VerbsIndex {
  total_verbs: number;
  verbs: Array<{
    rank: number;
    verb_english: string;
    verb_russian: string;
    verb_infinitive: string;
    folder_name: string;
  }>;
}

// Per-verb detailed index (minimal navigation data)
interface VerbIndex {
  verb_english: string;
  verb_russian: string;
  verb_infinitive: string;
  verb_rank: number;
  folder_name: string;
  examples: Array<{
    tense: string;
    pronoun: string;
    polarity: string;
    file_path: string;
  }>;
}

interface TenseLevelMapping {
  [tense: string]: string;
}

class DataLoader {
  private trainingExampleCache = new Map<string, TrainingExample>();
  private verbsIndex: VerbsIndex | null = null;
  private verbIndexCache = new Map<string, VerbIndex>();
  private tenseLevelMapping: TenseLevelMapping | null = null;

  async loadVerbsIndex(): Promise<VerbsIndex> {
    if (this.verbsIndex) {
      return this.verbsIndex;
    }

    try {
      console.log('Loading main verbs index...');
      const response = await fetch('/data/verbs_index.json');
      if (!response.ok) {
        throw new Error('Failed to load verbs index');
      }
      
      this.verbsIndex = await response.json();
      console.log('Verbs index loaded');
      
      return this.verbsIndex!;
    } catch (error) {
      console.error('Error loading verbs index:', error);
      throw error;
    }
  }

  async loadVerbIndex(folderName: string): Promise<VerbIndex> {
    if (this.verbIndexCache.has(folderName)) {
      return this.verbIndexCache.get(folderName)!;
    }

    try {
      const response = await fetch(`/data/output/verb_indexes/${folderName}.json`);
      if (!response.ok) {
        throw new Error(`Failed to load verb index for ${folderName}`);
      }
      
      const verbIndex: VerbIndex = await response.json();
      this.verbIndexCache.set(folderName, verbIndex);
      
      return verbIndex;
    } catch (error) {
      console.error(`Error loading verb index for ${folderName}:`, error);
      throw error;
    }
  }

  async loadTenseLevelMapping(): Promise<TenseLevelMapping> {
    if (this.tenseLevelMapping) {
      return this.tenseLevelMapping;
    }

    try {
      const response = await fetch('/data/tense_level_mapping.json');
      if (!response.ok) {
        throw new Error('Failed to load tense level mapping');
      }
      
      this.tenseLevelMapping = await response.json();
      return this.tenseLevelMapping!;
    } catch (error) {
      console.error('Error loading tense level mapping:', error);
      throw error;
    }
  }

  async loadTrainingExample(
    verbEnglish: string, 
    pronoun: string, 
    tense: string,
    polarity: 'positive' | 'negative' = 'positive'
  ): Promise<TrainingExample | null> {
    try {
      const verbsIndex = await this.loadVerbsIndex();
      const verbInfo = verbsIndex.verbs.find(v => v.verb_english === verbEnglish);
      
      if (!verbInfo) {
        console.warn(`Verb "${verbEnglish}" not found`);
        return null;
      }

      const verbIndex = await this.loadVerbIndex(verbInfo.folder_name);

      let example = verbIndex.examples.find(
        ex => ex.tense === tense && ex.pronoun === pronoun && ex.polarity === polarity
      );

      let actualTense = tense;
      let actualPronoun = pronoun;
      let actualPolarity = polarity;

      if (!example) {
        example = verbIndex.examples.find(
          ex => ex.tense === tense && ex.polarity === polarity
        );
        if (example) {
          actualPronoun = example.pronoun;
        }
      }

      if (!example) {
        const oppositePolarity = polarity === 'positive' ? 'negative' : 'positive';
        example = verbIndex.examples.find(
          ex => ex.tense === tense && ex.pronoun === pronoun && ex.polarity === oppositePolarity
        );
        if (example) {
          actualPolarity = oppositePolarity;
        }
      }

      if (!example) {
        example = verbIndex.examples.find(ex => ex.pronoun === pronoun);
        if (example) {
          actualTense = example.tense;
          actualPolarity = example.polarity as 'positive' | 'negative';
        }
      }

      if (!example) {
        example = verbIndex.examples[0];
        if (example) {
          actualTense = example.tense;
          actualPronoun = example.pronoun;
          actualPolarity = example.polarity as 'positive' | 'negative';
        }
      }

      if (!example) {
        return null;
      }

      const cacheKey = `${verbEnglish}-${actualPronoun}-${actualTense}-${actualPolarity}`;
      
      if (this.trainingExampleCache.has(cacheKey)) {
        return this.trainingExampleCache.get(cacheKey)!;
      }

      const filePath = `/${example.file_path}`;
      const response = await fetch(filePath);
      if (!response.ok) {
        return null;
      }

      const data: TrainingExample = await response.json();
      this.trainingExampleCache.set(cacheKey, data);
      
      return data;
      
    } catch (error) {
      console.error('Error loading training example:', error);
      return null;
    }
  }

  async getVerbsWithRanks(): Promise<Array<{ verb: string; rank: number; turkishInfinitive: string }>> {
    const verbsIndex = await this.loadVerbsIndex();
    return verbsIndex.verbs.map(v => ({
      verb: v.verb_english,
      rank: v.rank,
      turkishInfinitive: v.verb_infinitive
    }));
  }

  async getAvailableTenses(verbEnglish: string, languageLevel?: string): Promise<string[]> {
    const verbsIndex = await this.loadVerbsIndex();
    const verbInfo = verbsIndex.verbs.find(v => v.verb_english === verbEnglish);
    
    if (!verbInfo) {
      return [];
    }

    const verbIndex = await this.loadVerbIndex(verbInfo.folder_name);
    let tenses = [...new Set(verbIndex.examples.map(ex => ex.tense))];
    
    if (languageLevel && languageLevel !== 'All') {
      const tenseLevelMapping = await this.loadTenseLevelMapping();
      
      tenses = tenses.filter(tenseName => {
        const tenseLevel = tenseLevelMapping[tenseName];
        if (!tenseLevel) return false;
        
        if (tenseLevel === languageLevel) return true;
        
        if (languageLevel.includes('-')) {
          const [start, end] = languageLevel.split('-');
          return tenseLevel === start || tenseLevel === end;
        }
        
        return false;
      });
    }
    
    return tenses;
  }

  async getAvailablePronouns(
    verbEnglish: string, 
    tense: string, 
    polarity: 'positive' | 'negative' = 'positive'
  ): Promise<string[]> {
    const verbsIndex = await this.loadVerbsIndex();
    const verbInfo = verbsIndex.verbs.find(v => v.verb_english === verbEnglish);
    
    if (!verbInfo) {
      return [];
    }

    const verbIndex = await this.loadVerbIndex(verbInfo.folder_name);
    const pronouns = verbIndex.examples
      .filter(ex => ex.tense === tense && ex.polarity === polarity)
      .map(ex => ex.pronoun);
    
    if (pronouns.length === 0) {
      const oppositePolarity = polarity === 'positive' ? 'negative' : 'positive';
      const oppPronouns = verbIndex.examples
        .filter(ex => ex.tense === tense && ex.polarity === oppositePolarity)
        .map(ex => ex.pronoun);
      
      return oppPronouns;
    }
    
    return pronouns;
  }

  async getNextTense(verbEnglish: string, currentTense: string, languageLevel?: string): Promise<string | null> {
    const tenses = await this.getAvailableTenses(verbEnglish, languageLevel);
    const currentIndex = tenses.indexOf(currentTense);
    
    if (currentIndex === -1) return tenses[0];
    if (currentIndex >= tenses.length - 1) return tenses[0];
    
    return tenses[currentIndex + 1];
  }

  async getPrevTense(verbEnglish: string, currentTense: string, languageLevel?: string): Promise<string | null> {
    const tenses = await this.getAvailableTenses(verbEnglish, languageLevel);
    const currentIndex = tenses.indexOf(currentTense);
    
    if (currentIndex === -1) return tenses[tenses.length - 1];
    if (currentIndex <= 0) return tenses[tenses.length - 1];
    
    return tenses[currentIndex - 1];
  }

  async getNextPronoun(
    verbEnglish: string, 
    tense: string, 
    currentPronoun: string, 
    polarity: 'positive' | 'negative' = 'positive'
  ): Promise<string | null> {
    const pronouns = await this.getAvailablePronouns(verbEnglish, tense, polarity);
    const currentIndex = pronouns.indexOf(currentPronoun);
    
    if (currentIndex === -1) return pronouns[0];
    if (currentIndex >= pronouns.length - 1) return pronouns[0];
    
    return pronouns[currentIndex + 1];
  }

  async getPrevPronoun(
    verbEnglish: string, 
    tense: string, 
    currentPronoun: string, 
    polarity: 'positive' | 'negative' = 'positive'
  ): Promise<string | null> {
    const pronouns = await this.getAvailablePronouns(verbEnglish, tense, polarity);
    const currentIndex = pronouns.indexOf(currentPronoun);
    
    if (currentIndex === -1) return pronouns[pronouns.length - 1];
    if (currentIndex <= 0) return pronouns[pronouns.length - 1];
    
    return pronouns[currentIndex - 1];
  }

  clearCache(): void {
    this.trainingExampleCache.clear();
    this.verbIndexCache.clear();
    this.verbsIndex = null;
    this.tenseLevelMapping = null;
  }
}

export const dataLoader = new DataLoader();

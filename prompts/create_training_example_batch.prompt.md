# Turkish Language Training Example Generation (Batch Mode)

You are a Turkish language expert who creates training examples for language learners. Your task is to generate a complete set of training examples for ALL pronoun and polarity combinations for a given verb and tense.

{json_schema}

{grammar_rules}

## Task Parameters
- **Verb (English)**: {verb_english} (NOTE: English verb is provided WITHOUT the "to" prefix - e.g., "be", "have", "do")
- **Verb (Infinitive Turkish)**: {verb_infinitive}
- **Verb Tense**: {verb_tense}
- **Language Level**: {language_level}

{pronoun_requirements}

## Requirements for EACH Example

### 1. Conjugated Verb Form

Apply the grammar rules provided above to conjugate the verb correctly:

**For POSITIVE polarity:**
- Conjugate normally without negative affix
- Set "polarity": "positive"
- Set "negative_affix": null

**For NEGATIVE polarity:**
- Add the appropriate negative affix following the grammar rules
- Set "polarity": "negative"
- Set "negative_affix" to the actual affix used (e.g., "me", "ma", "mı", "mi")
- Structure: root + negative_affix + tense_affix + personal_affix
- Example: yapmıyorum = yap + mı + yor + um

**CRITICAL: Include buffer vowels in affixes**
- Buffer vowels (connecting vowels) MUST be included in the affix field where they appear
- **For şimdiki_zaman (present continuous):**
  - The tense marker is "yor" but it ALWAYS needs a buffer vowel before it
  - tense_affix MUST be: "iyor", "ıyor", "uyor", or "üyor" (following vowel harmony)
  - **NEVER just "yor"** - this is always wrong!
  
**Examples showing CORRECT affix breakdown:**
- gitmek → gidiyorum:
  - root: "git"
  - tense_affix: "**iyor**" (includes buffer vowel i)
  - personal_affix: "um"
  - ✅ Reconstruction: git + iyor + um = gidiyorum
  
- söylemek → söylüyorum:
  - root: "söyle"
  - tense_affix: "**üyor**" (includes buffer vowel ü)
  - personal_affix: "um"
  - ✅ Reconstruction: söyle + üyor + um = söylüyorum

### 2. Example Sentences - **VOCABULARY DIVERSITY IS CRITICAL**

**⚠️ MOST IMPORTANT RULE: Each of the 12 examples MUST use COMPLETELY DIFFERENT vocabulary!**

**Forbidden approach (DO NOT DO THIS):**
```
❌ ben: "Ben kitap okuyorum"
❌ sen: "Sen kitap okuyorsun"  
❌ o: "O kitap okuyor"
```
This is WRONG because it uses the same noun "kitap" for all examples!

**Required approach (DO THIS):**
```
✅ ben: "Ben büyük mavi kitabı okuyorum" (blue book)
✅ sen: "Sen ilginç gazete makalesini okuyorsun" (newspaper article)
✅ o: "O eski tarih dergisini okuyor" (history magazine)
✅ biz: "Biz önemli bilimsel raporu okuyoruz" (scientific report)
✅ siz: "Siz ünlü Türk romanını okuyorsunuz" (Turkish novel)
✅ onlar: "Onlar yeni çocuk hikayesini okuyorlar" (children's story)
```

**Vocabulary Diversity Requirements:**
1. **Different nouns** for each example (min 2 nouns per sentence)
   - Use varied objects, places, people, concepts
   - Example topics: food, nature, work, family, hobbies, travel, education, weather, emotions, daily activities

2. **Different adjectives** for each example (min 1 adjective per sentence)
   - Colors: kırmızı, mavi, yeşil, sarı, beyaz, siyah
   - Sizes: büyük, küçük, uzun, kısa
   - Qualities: güzel, çirkin, iyi, kötü, yeni, eski, temiz, kirli
   - Emotions: mutlu, üzgün, kızgın, sakin
   - Other: hızlı, yavaş, sıcak, soğuk, kolay, zor

3. **Different contexts** for each example
   - Vary the setting: home, school, park, office, restaurant, street, etc.
   - Vary the time: sabah, akşam, bugün, yarın, şimdi, her gün
   - Vary the manner: hızla, yavaşça, dikkatle, sessizce

4. **Varied sentence structures**
   - Don't just repeat the same pattern with different words
   - Use different word orders (while maintaining SOV preference)
   - Add time expressions, location markers, manner adverbs

**Turkish sentence requirements:**
- MUST contain the EXACT "verb_full" form generated
- **CRITICAL WORD COUNT REQUIREMENT:**
  - The sentence MUST have **at least 4 content words** (excluding pronouns)
  - Content words = nouns, adjectives, verbs (including the conjugated verb), adverbs, objects
  - DO NOT count: ben, sen, o, biz, siz, onlar
  - **Examples of counting:**
    - "Ben kitap okuyorum" = 2 words (kitap, okuyorum) ❌ FAIL - TOO SHORT
    - "Ben büyük mavi kitabı okuyorum" = 4 words (büyük, mavi, kitabı, okuyorum) ✅ PASS
    - "Küçük çocuk parkta mutlu oynuyor" = 5 words (küçük, çocuk, parkta, mutlu, oynuyor) ✅ PASS
  - **If your sentence has fewer than 4 content words, ADD more adjectives or nouns!**
- Use natural Turkish word order (Subject-Object-Verb preferred, but flexible)
- Appropriate complexity for {language_level} learners
- Natural, realistic language that native speakers would actually use

**English sentence requirements:**
- Natural translation that captures the meaning and context
- Use DIFFERENT vocabulary from other examples (match the Turkish diversity)
- Appropriate for {language_level} learners
- 4-8 words preferred

**Russian sentence requirements:**
- Natural translation with simple vocabulary
- Use DIFFERENT vocabulary from other examples (match the Turkish diversity)
- Maintain meaning and context from English/Turkish

### 3. Verification Before Output

Before generating the JSON output, verify:

1. ✓ All required pronoun+polarity combinations are present (check the Generation Requirements section above for the exact count)
2. ✓ Each example uses COMPLETELY DIFFERENT nouns (check: no repeated nouns across examples!)
3. ✓ Each example uses DIFFERENT adjectives (at least some variation)
4. ✓ Each example has a DIFFERENT context/setting
5. ✓ Each "verb_full" is correctly constructed following vowel harmony and affix rules
6. ✓ Each "tense_affix" includes buffer vowel where needed (especially for şimdiki_zaman!)
7. ✓ Each Turkish sentence has at least 4 content words (excluding pronouns)
8. ✓ Each Turkish sentence contains the exact "verb_full"
9. ✓ Polarity is correct: "positive" examples have no negative_affix, "negative" examples have negative_affix
10. ✓ Personal pronouns match the requirements (check Generation Requirements section above)

## Output Format

Return ONLY a valid JSON object with the "examples" array containing all required combinations. No markdown, no explanations, just the JSON.

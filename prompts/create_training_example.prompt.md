# Turkish Language Training Example Generation

You are a Turkish language expert who creates training examples for language learners. Your task is to generate realistic and natural training examples based on the provided verb, tense, and pronoun combination.

{json_schema}

{grammar_rules}

## Task Parameters
- **Verb (English)**: {verb_english} (NOTE: English verb is provided WITHOUT the "to" prefix - e.g., "be", "have", "do")
- **Verb (Infinitive Turkish)**: {verb_infinitive}
- **Verb Tense**: {verb_tense}
- **Personal Pronoun**: {personal_pronoun}
- **Polarity**: {polarity}
- **Language Level**: {language_level}

## Requirements

### 1. Conjugated Verb Form

Apply the grammar rules provided above to conjugate the verb correctly:

**Polarity: "{polarity}"**

- If polarity is "positive": Conjugate normally without negative affix
  - Set "polarity": "positive"
  - Set "negative_affix": null

- If polarity is "negative": Add the appropriate negative affix following the grammar rules
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
  
- yapmak → yapıyorum:
  - root: "yap"
  - tense_affix: "**ıyor**" (includes buffer vowel ı)
  - personal_affix: "um"
  - ✅ Reconstruction: yap + ıyor + um = yapıyorum

- **Verification formula**: 
  - verb_full.length = root.length + (negative_affix.length or 0) + tense_affix.length + (personal_affix.length or 0)
  - If this doesn't match, you missed a buffer vowel!

### 2. Example Sentences

Create three natural example sentences:

**Turkish sentence**:
- MUST contain the EXACT "verb_full" form generated
- **CRITICAL WORD COUNT REQUIREMENT:**
  - The sentence MUST have **at least 4 content words** (excluding pronouns)
  - Content words = nouns, adjectives, verbs (including the conjugated verb), adverbs, objects
  - DO NOT count: ben, sen, o, biz, siz, onlar
  - **Examples of counting:**
    - "Ben kitap okuyorum" = 2 words (kitap, okuyor) ❌ FAIL - TOO SHORT
    - "Ben küçük kedi seviyor" = 3 words (küçük, kedi, seviyor) ❌ FAIL - NEED 1 MORE WORD  
    - "Ben büyük mavi kitabı okuyorum" = 4 words (büyük, mavi, kitap, okuyor) ✅ PASS
    - "Küçük çocuk parkta mutlu oynuyor" = 5 words (küçük, çocuk, park, mutlu, oynuyor) ✅ PASS
  - **If your sentence has fewer than 4 content words, ADD more adjectives or nouns!**
- MUST include at least 2 nouns AND 1 adjective
- Use natural Turkish word order (SOV preferred)
- Use vocabulary appropriate for {language_level} level
- Total sentence length: 5-10 words (including pronouns)
- Use specific nouns (people, places, things) instead of generic pronouns

**English translation**: 
- Must match the Turkish sentence meaning exactly
- Use the same specific nouns as in Turkish
- Natural English sentence structure

**Russian sentence**:
- Must match the Turkish sentence meaning exactly
- Use the same specific nouns as in Turkish
- Natural Russian sentence structure

### 3. Diversity Requirement

**IMPORTANT**: Use different vocabulary and contexts for each example you generate.
- DO NOT just substitute pronouns in the same sentence
- DO use completely different scenarios, settings, and vocabulary
- Example of what NOT to do:
  - ❌ "Ben kitap okuyorum" / "Sen kitap okuyorsun" / "O kitap okuyor"
- Example of what TO do:
  - ✅ "Ben kahve içiyorum" / "Öğrenci ders çalışıyor" / "Çocuklar parkta oynuyor"

## FINAL VERIFICATION

Before generating output, verify:

1. ✅ Does the Turkish sentence contain the EXACT verb_full form?
2. ✅ Is polarity "{polarity}" correctly applied?
3. ✅ Does the Turkish sentence have at least 4 words (excluding pronouns)?
4. ✅ Does the Turkish sentence include at least 2 nouns and 1 adjective?
5. ✅ Are the affixes correctly broken down following the grammar rules?
6. ✅ Do buffer vowels appear in the correct affix fields?

If all checks pass, generate the JSON output now.

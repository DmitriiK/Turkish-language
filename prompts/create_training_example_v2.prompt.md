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

**MODAL AFFIX (for imkan_kipi / ability mood)**
- For imkan_kipi (ability/possibility), you MUST set the "modal_affix" field:
  - Positive: modal_affix = "abil" or "ebil" (2-way vowel harmony). Structure: root + modal_affix + tense_affix + personal_affix
    - Example: yapabilirim = yap + abil + ir + im (modal_affix="abil", tense_affix="ir")
    - Example: gidebiliyorum = git + ebil + iyor + um (modal_affix="ebil", tense_affix="iyor")
    - Example: yapabileceksin = yap + abil + ecek + sin (modal_affix="abil", tense_affix="ecek")
  - Negative: modal_affix = "ama" or "eme" (replaces abil/ebil). Structure: root + modal_affix + tense_affix + personal_affix
    - Example: yapamam = yap + ama + z... → but for ben: yapamam = yap + ama + (no z) + m. Set modal_affix="ama", tense_affix="", personal_affix="m". NOTE: for aorist negative, -z- is absent in ben and biz forms.
    - Example: yapamıyorum = yap + ama + ıyor + um (modal_affix="ama", tense_affix="ıyor")
    - Example: yapamayacaksın = yap + ama + yacak + sın (modal_affix="ama", tense_affix="yacak")
  - The default tense combination is aorist (-(ı|i|u|ü)r), but imkan_kipi can combine with ANY tense marker.
- For all OTHER tenses (not imkan_kipi): set "modal_affix" to null

**CRITICAL: Include buffer vowels in affixes**
- If a buffer vowel (i, ı, u, ü, a, e) appears between morphemes, include it in the relevant affix field
- For şimdiki_zaman: The tense_affix MUST include the buffer vowel + "yor" (e.g., "iyor", "ıyor", "uyor", "üyor")
  - Example: gidiyorum → git + **iyor** + um (NOT git + yor + um)
  - Example: söylüyorum → söyle + **üyor** + um (NOT söyle + yor + um)
  - Example: yapıyorum → yap + **ıyor** + um (NOT yap + yor + um)
- For other tenses: Include any connecting vowels in the tense_affix or personal_affix as appropriate
- Verification rule: verb_full.length MUST EQUAL root.length + (modal_affix.length or 0) + (negative_affix.length or 0) + tense_affix.length + (personal_affix.length or 0)
- If lengths don't match, you forgot to include a buffer vowel or the modal affix somewhere!

### 2. Example Sentences

Create three natural example sentences:

**Turkish sentence**:
- MUST contain the EXACT "verb_full" form generated
- **CRITICAL: MUST have at least 4 words (not counting the pronoun ben/sen/o/biz/siz/onlar)**
  - Count only: nouns, adjectives, adverbs, other verbs, objects
  - Example: "Ben kitap okuyor**um**" = only 2 words (kitap, okuyor) ❌ TOO SHORT
  - Example: "Ben **küçük kedi**yi sev**iyor**um" = 3 words (küçük, kedi, sev) ❌ STILL TOO SHORT
  - Example: "Ben **büyük mavi kitap**ı okuyor**um**" = 4 words (büyük, mavi, kitap, okuyor) ✅ CORRECT
- MUST include at least 2 nouns AND 1 adjective
- Use natural Turkish word order (SOV preferred)
- Use vocabulary appropriate for {language_level} level
- Total length: 5-10 words including pronoun
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
7. ✅ For imkan_kipi: Is modal_affix set (abil/ebil or ama/eme)? Is tense_affix the ACTUAL tense marker (ir, iyor, di, ecek, etc.) and NOT the modal suffix?

If all checks pass, generate the JSON output now.

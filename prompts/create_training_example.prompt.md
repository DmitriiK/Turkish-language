# Turkish Language Training Example Generation

You are a Turkish language expert who creates training examples for language learners. Your task is to generate realistic and natural training examples based on the provided verb, tense, and pronoun combination.

## Task Parameters
- **Verb (English)**: {verb_english}
- **Verb (Infinitive Turkish)**: {verb_infinitive} 
- **Verb Tense**: {verb_tense}
- **Personal Pronoun**: {personal_pronoun}
- **Polarity**: {polarity}
- **Language Level**: {language_level}

## Requirements

### 1. Conjugated Verb Form
**CRITICAL: The polarity parameter is "{polarity}". You MUST follow these rules:**

**If polarity is "positive":**
- Conjugate the verb normally without any negative affix
- Set "polarity": "positive" in the output
- Set "negative_affix": null in the output

**If polarity is "negative":**
- You MUST add the negative affix (me/ma/mı/mi/mu/mü) between the verb root and the tense suffix
- The negative affix MUST follow vowel harmony rules (e-type verbs use me/mi, a-type verbs use ma/mı/mu/mü)
- Set "polarity": "negative" in the output
- Set "negative_affix" to the actual negative affix used (e.g., "me", "ma", "mı", "mi")
- The sentences must convey a negative meaning
- **IMPORTANT**: The "tense_affix" should ONLY contain the tense marker, NOT the negative affix
- **IMPORTANT**: The "personal_affix" should ONLY contain the personal ending, NOT the tense marker

**Structure breakdown for negative verbs:**
- verb_full = root + negative_affix + tense_affix + personal_affix
- Example: olmayacağız = ol + ma + yacak + ız
  - root: "ol"
  - negative_affix: "ma"
  - tense_affix: "yacak" (future tense marker)
  - personal_affix: "ız" (1st person plural)
- Example: yapmıyorum = yap + mı + yor + um
  - root: "yap"
  - negative_affix: "mı"
  - tense_affix: "yor" (present continuous marker)
  - personal_affix: "um" (1st person singular)

**Examples of negative forms:**
- yapmak (to do) + şimdiki_zaman + ben → yapmıyorum (I'm not doing)
  - Breakdown: yap + mı + yor + um
  - negative_affix: "mı", tense_affix: "yor", personal_affix: "um"
- gelmek (to come) + şimdiki_zaman + o → gelmiyor (he/she is not coming)
  - Breakdown: gel + mi + yor (no personal affix for 3rd person present)
  - negative_affix: "mi", tense_affix: "yor", personal_affix: null
- gitmek (to go) + geçmiş_zaman + ben → gitmedim (I didn't go)
  - Breakdown: git + me + di + m
  - negative_affix: "me", tense_affix: "di", personal_affix: "m"
- olmak (to be) + geçmiş_zaman + ben → olmadım (I wasn't)
  - Breakdown: ol + ma + dı + m
  - negative_affix: "ma", tense_affix: "dı", personal_affix: "m"
- olmak (to be) + gelecek_zaman + biz → olmayacağız (we will not be)
  - Breakdown: ol + ma + yacak + ız
  - negative_affix: "ma", tense_affix: "yacak", personal_affix: "ız"
- **SPECIAL CASE - geniş_zaman (aorist) negative:**
  - yapmak (to do) + geniş_zaman + ben → yapmam (I don't do)
    - Breakdown: yap + ma + "" + m
    - negative_affix: "ma", tense_affix: "" (EMPTY - no visible tense marker in aorist negative), personal_affix: "m"
  - olmak (to be) + geniş_zaman + ben → olmam (I am not)
    - Breakdown: ol + ma + "" + m
    - negative_affix: "ma", tense_affix: "" (EMPTY), personal_affix: "m"
  - **NOTE:** In geniş_zaman negative, there is NO separate tense affix after the negative affix. Set tense_affix to empty string "" or null.

**General conjugation rules:**
- Apply the appropriate tense suffix for {verb_tense}
- Add the correct personal affix for {personal_pronoun}
- Follow Turkish vowel harmony rules
- Consider consonant changes and phonetic adaptations

### 2. Example Sentences
Create three natural example sentences:

**IMPORTANT: Use specific nouns instead of pronouns in the sentences**
- Instead of "He/She is a teacher" → use "My brother is a teacher", "The student is learning", "My friend likes coffee"
- Instead of "They are working" → use "The children are playing", "My parents are working", "The students are studying"

**Turkish sentence**:
- **⚠️ MINIMUM LENGTH: The sentence MUST have at least 4 words (not counting pronouns like ben/sen/o/biz/siz/onlar)**
- **⚠️ REQUIRED COMPONENTS: Must include at least 2 nouns AND at least 1 adjective**
- Include the conjugated verb form
- Use specific nouns (people, places, things) to create meaningful context
- Natural Turkish word order (SOV preferred)
- **CRITICAL: Must contain at least 4 words EXCLUDING the pronoun (ben/sen/o/biz/siz/onlar)**
  - ❌ WRONG (3 words): "Öğrenci başarılı oluyor" 
  - ✅ CORRECT (4 words): "Öğrenci bu yıl başarılı oluyor"
  - ✅ CORRECT (5 words): "Küçük çocuk parkta mutlu oluyor"
- Should contain 4-10 words total (not counting pronouns)
- If there is well known phrase with specified verb, like pronoun or something from song or poem, use them as example
- Use vocabulary appropriate for {language_level} level Turkish learners
- Contextually meaningful and realistic
- Avoid complex grammar structures beyond the target level

**English translation sentence**: 
- Must match the Turkish sentence meaning exactly
- Use the same specific nouns as in Turkish

**Russian sentence**:
- Must match the Turkish sentence meaning exactly
- Use the same specific nouns as in Turkish

## Important Notes
- **VERIFY POLARITY: The polarity is "{polarity}". If it's "negative", the verb MUST have a negative affix and the meaning MUST be negative.**
- Ensure all sentences are natural and would be used by native speakers
- The conjugated verb must be grammatically correct for the given tense and pronoun
- All three sentences should convey the same basic meaning
- Keep sentences simple and appropriate for {language_level} level learners
- Use only basic, common vocabulary suitable for {language_level} proficiency
- For A1/A2 levels: use high-frequency words, simple sentence structures
- Avoid complex vocabulary, idioms, or advanced grammatical constructions
- Make sure the Turkish sentence follows natural word order patterns
- Context should be familiar and relatable to language learners

## FINAL CHECK - VERIFY BEFORE GENERATING:

**MANDATORY REQUIREMENTS:**
1. ✅ Is polarity "{polarity}" correctly applied?
   - If negative: Does verb_full contain the negative affix? Is polarity field = "negative"? Is negative_affix filled?
   - If positive: Is verb_full without negative affix? Is polarity field = "positive"? Is negative_affix null?

2. ✅ **Does the Turkish sentence have AT LEAST 4 words (not counting the pronoun)?**
   - Count: Remove pronoun (ben/sen/o/biz/siz/onlar if present), then count remaining words
   - Must be ≥ 4 words
   - Example: "Öğrenci başarılı oluyor" = 3 words ❌ TOO SHORT - NEEDS 1 MORE WORD
   - Example: "Öğrenci bu yıl başarılı oluyor" = 4 words ✅ CORRECT

3. ✅ **Does the Turkish sentence include at least 2 nouns and 1 adjective?**
   - Must have 2+ nouns (people, places, things)
   - Must have 1+ adjective (descriptive word)

**IF ALL CHECKS PASS:** Generate the training example now.
**IF ANY CHECK FAILS:** Revise the sentence to meet ALL requirements, then generate.


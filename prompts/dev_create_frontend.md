Need to create Web Application to learn grammer forms of Turkish Verbs.
It should display  cards for learning.
One card displays data related to some verb, in particular tense, and for particular pronoun (if applicable).
Data we operate with looks like
```json
{
  "verb_rank": 2,
  "verb_english": "to come",
  "verb_russian": "приходить",
  "verb_infinitive": "gelmek",
  "turkish_verb": {
    "verb_full": "geldim",
    "root": "gel",
    "tense_affix": "di",
    "verb_tense": "geçmiş_zaman",
    "personal_pronoun": "ben",
    "personal_affix": "m"
  },
  "language_level": "A1",
  "english_example_sentence": "I came to the park.",
  "russian_example_sentence": "Я пришел в парк.",
  "turkish_example_sentence": "Ben parka geldim.",
}
```
Parameter of training session are:
  - "Direction": "English to Turkish" or "Russian to Turkish" or "Turkish to English" or "Turkish to Russian"
  Initially the car is loaded with blank texboxes for second language in this pair". 
  Thus, for "English to Turkish" we are displaying
  - verb_english verb
  - english_example_sentence
  - blank textbox for Turkish, where uses supposed to print turkish example
  User have possibility:
  -to print turkish verb or the whole sentence. Once he prints root of the verb correctly the app should notify user. Once it prints it with tense affix - it should be another notifications. Same for personal pronoun affix. and the last is the whole sentence.
  For notification use as separate list of ✅ .
  User can click on each of the checkboxes to have the correspondent part populated by app.

  To navigate to the next card user can move to several directions:
  - to the next verb
  - to the next tense
  - to the next personal pronoun

  Also application should have kind of pagination, based on verb rank, having numeric texbox to move to the verb to correspondent rank
  To support this navigation you can create separate json that would work kind of index.

  Non functional requirements: 
  - Use React framework


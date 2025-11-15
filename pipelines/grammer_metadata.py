from enum import StrEnum  # type: ignore
from typing import Literal, Optional
from pydantic import BaseModel, Field


class LanguageLevel(StrEnum):
    """Language proficiency levels for Turkish learners."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


class VerbPolarity(StrEnum):
    """Verb polarity - positive or negative form."""
    Positive = "positive"
    Negative = "negative"


class VerbTense(StrEnum):
    """
    Turkish verb tenses for conjugation patterns.
    
    Present tenses:
    - şimdiki_zaman: Present Continuous (yapıyorum - I am doing)
    
    Past tenses:
    - geçmiş_zaman: Simple Past (yaptım - I did)
    
    Future tenses:
    - gelecek_zaman: Simple Future (yapacağım - I will do)
    
    Habitual:
    - geniş_zaman: Simple Present/Habitual (yaparım - I do/make)
    """
    
    # Present tense forms
    ŞimdikiZaman = "şimdiki_zaman"
    
    # Past tense forms
    GeçmişZaman = "geçmiş_zaman"
    
    # Future tense forms
    GelecekZaman = "gelecek_zaman"
    Yaracağım = "yaracağım"
    
    # General/habitual tense
    GenişZaman = "geniş_zaman"
    
    # Modal forms
    IstekKipi = "istek_kipi"        # Yapayım - Let me do (Optative/Subj.)
    EmirKipi = "emir_kipi"          # Yap! - Do! (Imperative Mood)
    ŞartKipi = "şart_kipi"          # Yapsam - If I were to do (Conditional)
    
    # Necessity and ability
    GereklilikKipi = "gereklilik_kipi"    # Yapmam lazım - I need to (Necess.)
    İmkanKipi = "imkan_kipi"              # Yapabilirim - I can do (Ability)
    ZorunlulukKipi = "zorunluluk_kipi"    # Yapmalıyım - I must do (Oblig.)
    
    # Conditional forms
    GeçmişGelecekZaman = "geçmiş_gelecek_zaman"  # Yaracaktım - I was going to
    ŞartlıKipi = "şartlı_kipi"                   # Yaparsam - If I do (Cond.)
    FarzîGeçmişZaman = "farzî_geçmiş_zaman"      # Yaptıysam - If I did
    
    # Participial forms
    SıfatFiil = "sıfat_fiil"        # Yapan - doing/who does (Present Part.)
    ZarfFiil = "zarf_fiil"          # Yararak - by doing (Gerund)
    UlakFiil = "ulak_fiil"          # Yapıp - having done (Perfect Part.)
    
    # Temporal forms
    ZamanSıfatı = "zaman_sıfatı"    # Yaptığımda - when I do (Temporal Clause)


class VerbFormInfo(BaseModel):
    """Information about verb forms and their pronoun usage.
    
    type_of_personal_pronoun:
        - None: No pronouns (participles, infinitives)
        - 1: All pronouns (ben, sen, o, biz, siz, onlar) - regular verb forms
        - 2: All pronouns with possessive affixes (ben, sen, o, biz, siz, onlar)
        - 3: Imperative pronouns only (sen, siz, o, onlar) - excludes ben, biz
    """
    verb_tense: VerbTense
    language_level: LanguageLevel
    type_of_personal_pronoun: Literal[1, 2, 3] | None = None
    polarity: VerbPolarity = VerbPolarity.Positive  # Default to positive


# List of all VerbFormInfo instances
VERB_FORM_INFOS = [
    # Present tense forms - POSITIVE
    VerbFormInfo(
        verb_tense=VerbTense.ŞimdikiZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    # Present tense forms - NEGATIVE
    VerbFormInfo(
        verb_tense=VerbTense.ŞimdikiZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # Past tense forms - POSITIVE
    VerbFormInfo(
        verb_tense=VerbTense.GeçmişZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    # Past tense forms - NEGATIVE
    VerbFormInfo(
        verb_tense=VerbTense.GeçmişZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # Future tense forms - POSITIVE
    VerbFormInfo(
        verb_tense=VerbTense.GelecekZaman,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    # Future tense forms - NEGATIVE
    VerbFormInfo(
        verb_tense=VerbTense.GelecekZaman,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.Yaracağım,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.Yaracağım,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # General/habitual tense - POSITIVE
    VerbFormInfo(
        verb_tense=VerbTense.GenişZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    # General/habitual tense - NEGATIVE
    VerbFormInfo(
        verb_tense=VerbTense.GenişZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # Modal forms
    VerbFormInfo(
        verb_tense=VerbTense.IstekKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.IstekKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.EmirKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=3,  # Imperatives use sen, siz, o, onlar (not ben, biz)
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.EmirKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=3,  # Negative imperatives: Yapma! Yapmayın! Yapmasın! Yapmasınlar!
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ŞartKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ŞartKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # Necessity and ability
    VerbFormInfo(
        verb_tense=VerbTense.GereklilikKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.GereklilikKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.İmkanKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.İmkanKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZorunlulukKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZorunlulukKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # Conditional forms
    VerbFormInfo(
        verb_tense=VerbTense.GeçmişGelecekZaman,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.GeçmişGelecekZaman,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ŞartlıKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ŞartlıKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.FarzîGeçmişZaman,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.FarzîGeçmişZaman,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=1,
        polarity=VerbPolarity.Negative
    ),
    
    # Participial forms
    VerbFormInfo(
        verb_tense=VerbTense.SıfatFiil,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=None,  # "Yapan" - no personal affix needed
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.SıfatFiil,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=None,  # "Yapmayan" - negative participle
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZarfFiil,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=None,  # "Yaparak" - no personal affix
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZarfFiil,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=None,  # "Yapmadan" - negative adverbial
        polarity=VerbPolarity.Negative
    ),
    VerbFormInfo(
        verb_tense=VerbTense.UlakFiil,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=None,  # "Yapıp" - no personal affix
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.UlakFiil,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=None,  # "Yapmayıp" - negative converb
        polarity=VerbPolarity.Negative
    ),
    
    # Temporal forms
    VerbFormInfo(
        verb_tense=VerbTense.ZamanSıfatı,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=2,  # "Yaptığımda" - uses possessive affix
        polarity=VerbPolarity.Positive
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZamanSıfatı,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=2,  # "Yapmadığımda" - negative temporal
        polarity=VerbPolarity.Negative
    ),
]


class PersonalPronoun(StrEnum):
    Ben = "ben"
    Sen = "sen"
    O_Third = "o"  # Third person singular
    Biz = "biz"
    Siz = "siz"
    Onlar = "onlar"


class PersonalAffixTypeI(StrEnum):
    """Type I Personal Affixes (Used with verbs, some adjectives)
    Includes all vowel harmony variants"""
    
    # Ben variants: -ım, -im, -um, -üm
    Ben_im = "ım"
    Ben_i = "im"
    Ben_u = "um"
    Ben_u2 = "üm"
    
    # Sen variants: -sın, -sin, -sun, -sün
    Sen_a = "sın"
    Sen_i = "sin"
    Sen_u = "sun"
    Sen_u2 = "sün"
    
    # O (Third person) - no affix
    O_Third = ""
    
    # Biz variants: -ız, -iz, -uz, -üz
    Biz_a = "ız"
    Biz_i = "iz"
    Biz_u = "uz"
    Biz_u2 = "üz"
    
    # Siz variants: -sınız, -siniz, -sunuz, -sünüz
    Siz_a = "sınız"
    Siz_i = "siniz"
    Siz_u = "sunuz"
    Siz_u2 = "sünüz"
    
    # Onlar variants: -lar, -ler
    Onlar_a = "lar"
    Onlar_e = "ler"


class PersonalAffixTypeII(StrEnum):
    """Type II Personal Affixes (Possessive affixes)
    Includes all vowel harmony variants"""
    
    # Ben - always "m" after vowels
    Ben = "m"
    
    # Sen - always "n" after vowels
    Sen = "n"
    
    # O (Third person) variants: -sı, -si, -su, -sü, -ı, -i, -u, -ü
    O_Third_si = "sı"
    O_Third_si2 = "si"
    O_Third_su = "su"
    O_Third_su2 = "sü"
    O_Third_i = "ı"
    O_Third_i2 = "i"
    O_Third_u = "u"
    O_Third_u2 = "ü"
    
    # Biz variants: -mız, -miz, -muz, -müz
    Biz_a = "mız"
    Biz_i = "miz"
    Biz_u = "muz"
    Biz_u2 = "müz"
    
    # Siz variants: -nız, -niz, -nuz, -nüz
    Siz_a = "nız"
    Siz_i = "niz"
    Siz_u = "nuz"
    Siz_u2 = "nüz"
    
    # Onlar variants: -ları, -leri
    Onlar_a = "ları"
    Onlar_e = "leri"


class TurkishVerb(BaseModel):
    verb_full: str = Field(
        description="Turkish verb with all affixes applied (e.g., 'gittim', 'konuşuyorum', 'okuyorum')"
    )
    root: str = Field(
        description="Verb root without any affixes (e.g., 'git', 'konuş')"
    )
    tense_affix: str = Field(description="Tense affix applied to the root (e.g., 'ti' for past tense)")
    verb_tense: VerbTense = Field(description="The grammatical tense used for conjugation")

    personal_pronoun: Optional[PersonalPronoun] = Field(description="Personal pronoun used with the verb (None for impersonal forms)")
    personal_affix: Optional[str] = Field(
        description="Personal affix applied with correct vowel harmony (e.g., 'um', 'sın', 'm', 'lar')"
    )
    polarity: VerbPolarity = Field(
        default=VerbPolarity.Positive,
        description="Verb polarity - positive or negative form"
    )
    negative_affix: Optional[str] = Field(
        default=None,
        description="Negative affix if the verb is negated (e.g., 'me', 'ma')"
    )


class TrainingExample(BaseModel):
    """A training example with nested Turkish verb structure for comprehensive LLM structured output."""
    
    # Basic verb information
    verb_rank: Optional[int] = Field(
        description="Frequency rank of the verb (lower numbers = more common)"
    )
    verb_english: str = Field(
        description="English infinitive verb without 'to' (e.g., 'go', 'speak')"
    )
    verb_russian: str = Field(
        description="Russian infinitive verb (e.g., 'идти', 'говорить')"
    )
    verb_infinitive: str = Field(
        description="Turkish infinitive verb (e.g., 'olmak', 'gitmek')"
    )
    
    # Nested Turkish verb conjugation structure
    turkish_verb: TurkishVerb = Field(
        description="Complete Turkish verb conjugation with all grammatical components"
    )

    # Example sentences
    english_example_sentence: str = Field(
        description="Natural English sentence using the verb (4-8 words) appropriate for the language level"
    )
    russian_example_sentence: str = Field(
        description="Russian equivalent of the English sentence with simple vocabulary"
    )
    turkish_example_sentence: str = Field(
        description="Turkish sentence using the conjugated verb with natural word order (SOV preferred)"
    )
    
    @property
    def turkish_example_sentence_with_blank(self) -> str:
        """Generate the Turkish sentence with blank where the conjugated verb should be"""
        return self.turkish_example_sentence.replace(self.turkish_verb.verb_full, "______")


class BatchTrainingExamples(BaseModel):
    """Batch of training examples for a single verb + tense combination.
    
    Contains all pronoun × polarity combinations (typically 12 examples):
    - 6 pronouns (ben, sen, o, biz, siz, onlar) × 2 polarities (positive, negative)
    
    For special cases:
    - Imperatives: 4 pronouns (sen, o, siz, onlar) - excludes ben, biz
    - Participles: 1 example (no personal pronouns)
    """
    examples: list[TrainingExample] = Field(
        description="List of training examples for all pronoun+polarity combinations"
    )


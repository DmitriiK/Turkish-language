from enum import StrEnum  # type: ignore
from typing import Literal
from pydantic import BaseModel


class LanguageLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class VerbTense(StrEnum):
    # Present tense forms
    ŞimdikiZaman = "şimdiki_zaman"  # Yapıyorum - I am doing (Present Cont.)
    
    # Past tense forms
    GeçmişZaman = "geçmiş_zaman"    # Yaptım - I did (Simple Past)
    
    # Future tense forms
    GelecekZaman = "gelecek_zaman"  # Yapacağım - I will do (Simple Future)
    Yaracağım = "yaracağım"         # Yapacağım - I will do (Definite Future)
    
    # General/habitual tense
    GenişZaman = "geniş_zaman"      # Yaparım - I do/make (Simple Present)
    
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
    verb_tense: VerbTense
    language_level: LanguageLevel
    type_of_personal_pronoun: Literal[1, 2] | None = None


# List of all VerbFormInfo instances
VERB_FORM_INFOS = [
    # Present tense forms
    VerbFormInfo(
        verb_tense=VerbTense.ŞimdikiZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1
    ),
    
    # Past tense forms
    VerbFormInfo(
        verb_tense=VerbTense.GeçmişZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1
    ),
    
    # Future tense forms
    VerbFormInfo(
        verb_tense=VerbTense.GelecekZaman,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1
    ),
    VerbFormInfo(
        verb_tense=VerbTense.Yaracağım,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1
    ),
    
    # General/habitual tense
    VerbFormInfo(
        verb_tense=VerbTense.GenişZaman,
        language_level=LanguageLevel.A1,
        type_of_personal_pronoun=1
    ),
    
    # Modal forms
    VerbFormInfo(
        verb_tense=VerbTense.IstekKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1
    ),
    VerbFormInfo(
        verb_tense=VerbTense.EmirKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=None  # Imperatives don't use personal affixes
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ŞartKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1
    ),
    
    # Necessity and ability
    VerbFormInfo(
        verb_tense=VerbTense.GereklilikKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=None  # "Yapmam lazım" - no personal affix
    ),
    VerbFormInfo(
        verb_tense=VerbTense.İmkanKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZorunlulukKipi,
        language_level=LanguageLevel.A2,
        type_of_personal_pronoun=1
    ),
    
    # Conditional forms
    VerbFormInfo(
        verb_tense=VerbTense.GeçmişGelecekZaman,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=1
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ŞartlıKipi,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=1
    ),
    VerbFormInfo(
        verb_tense=VerbTense.FarzîGeçmişZaman,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=1
    ),
    
    # Participial forms
    VerbFormInfo(
        verb_tense=VerbTense.SıfatFiil,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=None  # "Yapan" - no personal affix needed
    ),
    VerbFormInfo(
        verb_tense=VerbTense.ZarfFiil,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=None  # "Yararak" - no personal affix
    ),
    VerbFormInfo(
        verb_tense=VerbTense.UlakFiil,
        language_level=LanguageLevel.B1,
        type_of_personal_pronoun=None  # "Yapıp" - no personal affix
    ),
    
    # Temporal forms
    VerbFormInfo(
        verb_tense=VerbTense.ZamanSıfatı,
        language_level=LanguageLevel.B2,
        type_of_personal_pronoun=2  # "Yaptığımda" - uses possessive affix
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
    """Type I Personal Affixes (Used with verbs, some adjectives)"""
    Ben = "ım"      # -ım, -im, -um, -üm (ben yorgunum - I am tired)
    Sen = "sın"     # -sın, -sin, -sun, -sün (sen yorgunsun - you are tired)
    O_Third = ""    # no affix (o yorgun - he/she is tired)
    Biz = "ız"      # -ız, -iz, -uz, -üz (biz yorgunuz - we are tired)
    Siz = "sınız"   # -sınız, -siniz, -sunuz, -sünüz (siz yorgunsunuz)
    Onlar = "lar"   # -lar, -ler (onlar yorgunlar - they are tired)


class PersonalAffixTypeII(StrEnum):
    """Type II Personal Affixes (Possessive affixes)"""
    Ben = "m"       # -m (evim - my house, after vowels)
    Sen = "n"       # -n (evin - your house, after vowels)
    O_Third = "sı"  # -sı, -si, -su, -sü, -ı, -i, -u, -ü (evi - his/her house)
    Biz = "mız"     # -mız, -miz, -muz, -müz (evimiz - our house)
    Siz = "nız"     # -nız, -niz, -nuz, -nüz (eviniz - your house)
    Onlar = "ları"  # -ları, -leri (evleri - their house)


class TrainingExample:
    noun: str  # noun in turkish, initial form
    verb_tense: VerbTense
    personal_pronoun: PersonalPronoun
    english_example_sentence: str
    russian_example_sentence: str
    turkish_example_sentence: str
    turkish_example_sentence_with_blank: str



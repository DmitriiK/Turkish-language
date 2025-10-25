# Turkish Language Learning System

A comprehensive system for learning Turkish grammar forms and verb conjugations, featuring an AI-powered training example generator and a modern React frontend application.

## 🚀 Quick Start

### Frontend Application (React)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Backend Pipeline (Python)
```bash
# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install langchain langchain-google-genai python-dotenv pydantic

# Configure API key (create .env file)
echo "GEMINI_API_KEY=your_key_here" > .env

# Generate training examples
python pipelines/create_traing_example.py --language-level A2 --top-n-verbs 5
```

## 📁 Project Structure

```
Turkish-language/
├── frontend/                 # React web application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── types/           # TypeScript definitions
│   │   ├── utils/           # Utility functions
│   │   └── App.tsx         # Main application
│   ├── public/             
│   │   └── data/           # Symlinked training data
│   ├── package.json
│   └── vite.config.ts
├── pipelines/               # AI training data generation
│   ├── create_traing_example.py
│   ├── grammer_metadata.py
│   └── README.md
├── data/
│   ├── input/
│   │   └── verbs.csv       # 300 most common Turkish verbs
│   └── output/
│       └── training_examples_for_verbs/  # Generated examples
├── prompts/                # AI prompt templates
├── tests/                  # Test suite
└── config.toml            # Configuration
```

## 🎯 Features

### Interactive Learning App
- **Progressive Feedback**: Get checkmarks for verb roots, tense affixes, personal affixes, and complete sentences
- **Multiple Learning Directions**: English↔Turkish, Russian↔Turkish
- **Smart Navigation**: Browse by verb rank, tense, or pronoun
- **Progress Tracking**: Monitor streaks and accuracy
- **Responsive Design**: Works on desktop and mobile

### AI-Powered Content Generation
- **Structured Output**: Generates grammatically correct Turkish verb conjugations
- **Multi-language Support**: Creates examples in English, Russian, and Turkish
- **Language Level Awareness**: Adapts vocabulary complexity (A1-B2)
- **Comprehensive Coverage**: 18+ verb tenses and forms

## 🛠️ Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Framer Motion (animations)

**Backend:**
- Python 3.12+
- LangChain (AI framework)
- Pydantic (data validation)
- Azure OpenAI / Google Gemini

## 📚 Learning Content

### Verb Coverage
- 300 most common Turkish verbs
- All major tenses (present, past, future, conditional, etc.)
- 6 personal pronouns + impersonal forms
- Language levels A1 through B2

### Grammar Topics Covered
- Verb conjugations and affixes
- Vowel and consonant harmony
- Personal pronouns and their usage
- Tense formation patterns
- Progressive feedback on accuracy

## 🎓 Usage Examples

### Learning Turkish Verbs
1. Select learning direction (e.g., "English → Turkish")
2. View English verb and sentence: "I am reading" → "Ben kitap okuyorum"
3. Type the Turkish translation
4. Get progressive feedback:
   - ✅ Verb root "oku" identified
   - ✅ Present tense affix "uyor" correct
   - ✅ Personal affix "um" correct
   - ✅ Complete sentence perfect!

### Generating Training Data
```bash
# Generate A1 level examples for top 10 verbs
python pipelines/create_traing_example.py --language-level A1 --top-n-verbs 10

# Generate B2 level examples for top 50 verbs  
python pipelines/create_traing_example.py --language-level B2 --top-n-verbs 50
```

## 🔧 Development Setup

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- Google Gemini or Azure OpenAI API key

### Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd Turkish-language

# Frontend setup
cd frontend
npm install
npm run dev

# Backend setup (in new terminal)
cd ..
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
```

## 🚀 Deployment

### Frontend (Static Hosting)
```bash
cd frontend
npm run build
# Deploy 'dist' folder to Vercel, Netlify, etc.
```

### Backend (Cloud Functions)
- Deploy as serverless functions
- Set environment variables for API keys
- Configure CORS for frontend access

## 📈 Performance

- **Fast Loading**: Optimized bundle sizes with code splitting
- **Efficient Data**: JSON-based training examples with caching
- **Responsive UI**: 60fps animations with Framer Motion
- **Smart Caching**: Reduces API calls and improves UX

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices
- Write tests for new features
- Use conventional commit messages
- Ensure responsive design
- Maintain accessibility standards

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Turkish language grammar resources
- OpenAI/Google for AI capabilities
- React and TypeScript communities
- Contributors and language learners

---

## Original Grammar Documentation

- [Links](#links)
- [ Şimdiki zaman](#Şimdiki-zaman)
- [Cases](#cases)
- [Consonant harmony](#Consonant-harmony)
- [Belirtme Hâli (Определительный падеж, Accusative Case)](#Belirtme-Hâli)
- [Bulunma Hâli, Местный падеж, Locative case](#Bulunma-Hâli)
- [Yönelme Hâli. Направительный падеж](#Yönelme-Hâli)
- [Ayrılma Hâli. Исходный падеж](#Ayrılma-Hâli)
- [Possessive pronouns (aффиксы принадлежности)](#possessive-pronouns)
- [Изафеты](#isafetes)
- [Dıktan sonra and madan önce](#dıktan-sonra-and-madan-önce)
- [Time](#time)
- [görülen/belirmi geçmiş zaman ( Past tense)](#geçmiş-zaman)
- [Gelecek zaman (future tense)](#Gelecek-zaman)
- [Dan beri; DIr (For. Since; For)](#Dan-Beri-and-DIr)
- [ki](#ki)
- [Comparison (Сравнения: daha, az, en)](#Comparison)
- [Kendi (свой, самому)](#Kendi)
- [Imperatives (повелительное наклонение, Emir kipi)](#Imperatives)
- [Comparison (kadar и gibi)](#Comparison-kadar-gibi)
---
# Links
[Турецкий язык с нуля, от Елены Крупновой, "SEVE SEVE TÜRKÇE Турецкий в радость"](https://www.youtube.com/playlist?list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP)
---
# Şimdiki zaman 
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/ec260874-e9b9-4958-8a50-ff7dd29cb958)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/bc68e389-b186-4d59-a320-a71709b12f91)

# Cases
1. **Nominative Case (Yalın Hâl)**: This is the default case used for the subject of a sentence. It has no affix.
   - Questions: "Who?" (Kim?), "What?" (Ne?)
   - Examples:
     - **Çocuk** parka gitti. (The child went to the park.)
     - **Kitap** masanın üstünde. (The book is on the table.)

2. **Accusative Case (Belirtme Hâli)**: This is used for the direct object of a sentence.
   - Affix: (y?) (ı | i | u |‑ü)
   - Questions: "Whom?" (Kimi?), "What?" (Neyi?)
   - Beni, Seni, Onu, Bezi, Sizi, onlary
   - Examples:
     - Elmayı yedim. (I ate the apple.)
     - Kitabı okudum. (I read the book.)
     - Arabayı sürdü. (He/she drove the car.)
     - Biz bu soruyu birlikte çözüyoruz. (We solve this question together)

3. **Dative Case (Yönelme Hâli)**: This is used to indicate direction or the indirect object.
   - Affix: ‑a, ‑e
   - Question: "To whom?" (Kime?), "To what?" (Neye?)
   - Examples:
     - Okula gidiyorum. (I am going to school.)
     - Sana mektup yazdım. (I wrote a letter to you.)
     - Eve geldim. (I came home.)

4. **Locative Case (Bulunma Hâli)**: This is used to specify location.
   - Affix: ‑da, ‑de
   - Question: "Where?" (Nerede?)
   - Notes: In the third person singular and plural, put the conjunctive letter 'n', -kıtabı_n_da 
   - Examples:
     - Odada kitaplar var. (There are books in the room.)
     - Parkta oynuyorum. (I am playing in the park.)
     - Denizde yüzdük. (We swam in the sea.)
     - Onun kıtabında çok ilginç bilgiler var.

5. **Ablative Case (Çıkma Hâli)**: This is used to indicate movement away from something.
   - Affix: ‑dan, ‑den
   - Question: "From where?" (Nereden?)
   - Examples:
     - Evden çıktım. (I left the house.)
     - Arabadan indim. (I got out of the car.)
     - Okuldan geliyorum. (I am coming from school.)

6. **Genitive Case (İyelik Hâli)**: This is used to show possession.
   - Affix: ‑(n)ın, ‑(n)in, ‑(n)un, ‑(n)ün
   - Question: "Whose?" (Kimin?), Neyin
   - Examples:
     - Ahmet'in arabası güzel. (Ahmet's car is nice.)
     - Kadının çantası kaybolmuş. (The woman's bag is lost.)
     - Çocuğun oyuncağı bozuk. (The child's toy is broken.)
     - Evin kapısı
     - Suyun üzeri (Water surface, (exception case)
   
7. **Падеж средства Vasıta Hâli** (~ Творительный)
- Affix:  ile, (y)la, (y)le
- Question: - with what? with whom
- Examples:
     - Sen kaşık ile yiyorsun = Sen kaşıkla yiyorsun
     - Ben kalem ile yaziyorum = Ben kalemle yaziyorum
     - O araba ile geliyour = O arabayla geliyor
     - Ben seninle evleniyourum
- Personal pronouns: benimle, senimle, onunla, bizimle, sizinle, onlarla
- Note: ile = "and", like "annem ile babam bugün okula geliyorlar"

8. **Eşitlik  Hâli** Эквативный падеж
- Affix: ca, ce, ça, çe
- Questions: Kimce, Nasil, Nece (По чьему мнению, Каким образом, На каком языке)
- Examples:
     - Cin ->Cince
     - Turk -> Turkçe
     - ailece - with all family
     - erkek-erkekçe
     - saatlerce - for many hours
     - sessizce - silently
 
  # Consonant harmony
- *fıstıkçı Şahap - f   s   t   k   ç   ş   h   p*.  If you add a suffix beginning with a "c" or a "d to a word ending in one of these hard consonants,
  then the c changes to a ç and the d to a t.
   - İngiliz (English [as an adjective]) –> İngilizce (English [the language])
   - Türk (Turkish [as an adjective]) –> Türkçe (Turkish [the language])
   - Park (park) –> Parkta (at the park)

- *c -> ç, d -> t, b -> p, and ğ -> k* at the end of words. Words should not end with certain letters(c, d, b, and ğ), and so consequently words which would ordinarily end with those letters get modified. However, if you add a vowel onto the end of them, they revert to their original form.

   - ağaç -> ağaca (to the tree) (when a suffix beginning with a vowel is added)
   - Dert (problem) -> derdimiz (our problem)
   - terlik (slipper) -> terliği (his/her slipper)
     
  **Note: if a suffix beginning with a consonant is added, the word remains in its modified form. e.g. terlikleri (his/her slippers)**
 ---
 # Belirtme Hâli
 [Урок 21. Belirtme Hâli. Определительный падеж.](https://www.youtube.com/watch?v=rPHldkFL1Ks&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=22)
 - *(y?) (ı | i | u |‑ü)*
 - Неоформленный определительный падеж без афикса(kalem alıyorum), аналог неопр. артикля. Оформленный, - когда указывается на конкретный инстанс класса
      - Bu kalem**i** alıyorum
      - Bu kalemin**i** alıyorum (С аффиксом принадлежности всегда используется
      - Kalemler*i* alıyorum. For plural always need to use
      - Ayşe'**ye** bekliyorum. Для имент собственных тоже  нужен всегда
 ___
  # Bulunma Hâli
  *(da|de)|(ta|te)*  **(fıstıkçı Şahap for t)*

  Personal pronouns: bende, sende, onda, bizde, sizde, onlarda

![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/0df85a05-1868-45fe-b083-e8f25e9abcf3)
  - Senden kalem var mı? Evet, bende kalem var. Onun arabase var mı?
  - Ben üniversitede  okuyorum
  ---
# Yönelme Hâli
- [Урок 19 Yönelme Hâli. Направительный падеж](https://www.youtube.com/watch?v=RWkQpMVP3ls&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=20) 
- * (y?)(a|e)*: Гармония на 2. Если последняя буква гласная - через "y". Озвоночение согласных ( c -> ç, d -> t, b -> p, and ğ -> k)
- Похоже на дательный падеж (ben sana inanıyorum), но не всегда (o bana kızıyor - он злится на меня).
- bana, sana, ona, bize, size, onlara
- Examples:
     - Ben arkadaşıma  yardım ediyorum. Я помогаю моему другу.
     - O şimdi işe gidiyor. Он/она сейчас идет на работу.
     - Kızlar çiçeğe bakıyorlar.   Девочки смотрят на цветок.
___
# Ayrılma Hâli
[Урок 20 Ayrılma Hâli. Исходный падеж. Падежи турецкого языка. Турецкий язык с нуля](https://www.youtube.com/watch?v=_zv8ih6_xvE&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=21)
- * (dan|den)|(tan\ten)*: Гармония на 2. "t"- после глухих согласных.
- Похоже на родительский падеж с предлогами "от", "из", "с", "из-за", но не всегда. 
- benden, senden, ondan, bizden, sizden, onlardan
- Examples:
   - Onlardan hiç kimse pikniğe gidiyor. Никто из них не собирается на пикник.
   - Siz bizden hoşlanıyor musunuz? Мы вам нравимся?
   - Biz senden bahsediyoruz.Мы беседуем о тебе.
---
# Possessive pronouns
| Pronoun | Vowels | Consonants |Vowels | Consonants |
|---------|---------------------|-----------------------|--------------------|------------------------|
| benim   | -m                  | -im/-ım/-um/-üm       | ev*im* (my house)    | araba*m* (my car)        |
| senin   | -n                  | -in/-ın/-un/-ün       | ev*in* (your house)  | araba*n* (your car)      |
| onun    | -si/-sı/-su/-sü     | -i/-ı/-u/-ü           | ev*i* (his/her house)| araba*sı* (his/her car)  |
| bizim   | -miz/-mız/-muz/-müz | -imiz/-ımız/-umuz/-ümüz| ev*imiz* (our house) | araba*mız* (our car)     |
| siz     | -niz/-nız/-nuz/-nüz | -iniz/-ınız/-unuz/-ünüz| ev*iniz* (your house)| araba*nız* (your car)    |
| onlar   | -leri/-ları or -si/-sı/-su/-sü |-leri/-ları or -i/-ı/-u/-ü  | evleri (their house) | araba*ları* (their car) |
---
# Isafetes
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/713b833d-8840-437f-b7c3-bbdd4361a716)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/cc5f06a1-488c-461a-989f-57fab62a830b)

## Изафетные цепочки
Name of friend of brother of Ailin is.
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/c4c69ac0-ed03-4212-ad6b-518e8864d270)
## Одноаффиксный изафет.
Первое слово - как класс предметов, на русском - прилагательное
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/b9e889a5-461d-4d30-b4fa-6a6685ab8afc)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/7949861c-d017-4071-9203-19849e863f37)
## Безафиксный изафет
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/c1ad9435-77c2-4235-829a-5ca485f66105)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/45610d86-5858-44f1-a1e1-01a954cc1a0c)
## Изафеты с местоимениями принадлежности
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/ee1c7285-7b2d-4f99-8162-b19f195d6642)
## Сочетания с падежными аффиксами
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/a54b045b-d002-458a-aa9a-a96e7cbfa356)
---
# [Послелоги göre, kadar, önce, sonra в турецком языке. Турецкий язык с нуля](https://www.youtube.com/watch?v=8zJYv1ynTS0&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=27)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/866c129e-72e9-43b1-90e4-3b4da7770e9d)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/25f33798-0832-450e-a71d-ec2e325f55b0)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/537fd13f-c034-4af3-b835-0e905aa5ba91)
___
# dıktan sonra and madan önce 
[Урок 27. Конструкции -dıktan sonra и -madan önce. Турецкий язык с нуля.](https://www.youtube.com/watch?v=iPzPYCCPBIw&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=28)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/1b369c8b-8623-45b9-9531-49d4e03b3db8)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/a67ffefe-ba08-4078-93c7-9a569aa223fc)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/b589d120-84a1-4770-bfc8-60ebc54e7fb1)
Examples:
- Film seyretmeden önce bilet alıyorum. — Перед тем, как посмотреть фильм, я покупаю билет. 
-  Duş yaptıktan sonra giyiniyor. — Приняв душ (после того, как он/она принимает душ), он/она одевается. 
-  Sınava girdikten sonra parti yapıyoruz. — Сдав экзамен (после того, как мы сдаем экзамен), устраиваем вечеринку. 
-  Sen uyumadan önce kitap okuyor musun? — Ты до того, как уснуть, читаешь книгу?
- İşim bittikten sonra eve gidiyorum. — После того, как моя работа заканчивается, я иду домой.
___
# Time
[Урок 28. Который час? Saat kaç? Время. Турецкий язык с нуля](https://www.youtube.com/watch?v=2stUqe2W6v4&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=29)
   ![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/4fb2ac00-741f-4874-9475-97cee5384140)
   - 13:30 : Saat bir buçuk
   - 07:30 : Sabah Saat yedi bucuk
   -  Ders yarım saat sonra baslıor : Lesson begins in half an - hour

![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/3b7adef5-0e47-4753-8744-cd9923598a4b)

- geçıyour saat [hours]+(Y)A<sup>4</sup> [minutes] geçıyour
   - 07:05 saat yedıye beş geçıyour
   - 08:10 saat sekizi on geçıyour
   - 09:10 saat dokuzu çeyrek geçıyour
   - 16:25 saat dordu yirmi beş eçıyour
- var : saat [hours]+(Y)A<sup>2</sup> [minutes] var. Dative Case (Yönelme Hâli)
     - 10:50 saat on ikiye on var
     - 15:45 saat dörde ceyrek var
     - 9:50 saat ona yirmi beş var
- at what time? Locative Case (Bulunma Hâli)
  - at 11:30 : on bir buçuk<ins>ta</ins>
  geçiyour ->geçe; var -> kala
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/ac8f0cdf-fa9f-44ac-9f5e-2a24090e038a)


# geçmiş zaman
[Урок 29. Прошедшее время на -dı. Часть 1. Турецкий с нуля](https://www.youtube.com/watch?v=2stUqe2W6v4&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=29 )
Прошедшее категорическое время
-d<sup>2</sup>ı<sup>4</sup>
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/c91275be-bdf0-47ca-a56a-49f9327500be)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/b7a0c6d7-9591-46ac-a95a-30a555cba290)
- Sen balık tuttun Ты ловил рыбу
- dun eve gitmeden önce alışveriş yaptık. Вчера перед приходом домой мы шопились
- kahvaltı yaptıktan sonra işe gitti. after having breakfast, he went to work
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/8db2fc0e-900d-472b-97a3-7637b13da72a)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/a4200fb1-9784-4ad5-982b-b907ea1aacde)
- ben dün okula gitmedim. ben dün okula gitmedim
- siz geçen yaz tatıl yapmadınız. you didn't take a vacation last summer
- Onlar geçen sene hiç çalışmadılar. They didn't work at all last year
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/2b6fc0c3-1c3e-470d-8821-e99c72d55b9b)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/f4f0b135-ef62-4ff9-873b-30b34e534283)
- O bizi davet ettim mi? Did he invite us?
- Siz yoruldunuz mu? Are you tired? Evet. Bız yorulduk. Hayır. Bız yorulmadık.
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/fed47e85-1221-446b-a4c0-6165bf0f06a2)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/3568d185-960a-494c-bd09-a957b2614e97)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/1aae2fbd-e004-4057-92ec-cfddf662e42f)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/0d63c9ab-a236-4059-a9ce-61031245fe65)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/5a849515-19b5-4ed1-bfdf-4c55b1ebe7d7)
- Dün çok yorgundum. I was very tired yesteday.
- çorbam sıcaktı. My soup was hot
- Sen hiç mutlu değildım. You was never happy
- Senin annem doctor muydu? Were your mather a doctor?
- Siz hafta sony evde miydiniz? Were you at home on weekend?

# Gelecek zaman
[Урок 31 Будущее время турецкого языка. Турецкий с нуля](https://www.youtube.com/watch?v=2stUqe2W6v4&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=29 )
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/d252f03d-5574-4aec-891e-912988cc5247)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/4927af5f-4567-482b-aecb-014dff680a85)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/0c71e852-687e-4b9c-8bfd-187c83e8fc2e)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/8210b9aa-d088-4263-9834-fce8fcb69a22)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/4460852c-16a6-408a-848b-79ad209cf505)
- Gelecek yıl yenı araba alacağım. Next year I'll buy a new car.
- Yarın bıraz  geç kalacaklar. They'll be a little late tomorrow
- Sız iki yıl sonra üniversiteden mezun olacaksınız. You will graduate from university in two years
  ![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/78452f68-0692-4b88-8af1-be26c88ce188)
- Ben sizinle tatile çıkmayacağım. I'm not going on vacation with you
artık konuşmayacağız, yapacağız. we won't talk anymore, we'll do
- Biz dışarıda beklemeyeceğiz. We will not wait outside
- ![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/f58aa6eb-0d35-4e61-aeb4-f843900f29d0)
- Sen bana yardim edecek misin? Will you help me? Evet, ben sana yardım edeceğim. Hayır, ben sata yardım etmeyeceğim
- Siz alışveriş yapacak mısınız? Will you go shoppoing.

# Dan beri and DIr
[Урок 32. Продолжительность действия. -DAn beri / - DIr. Турецкий с нуля](https://www.youtube.com/watch?v=IGUZzpESdpw&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=35)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/1d41f06b-eadb-4e9f-aa10-d16dc1983d14)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/3fe37460-3163-4599-94c1-6fdc6f3147ca)
**Note: "DAn" beri is equal to "DIr" (for..) if the beginning moment is not specified:"**
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/54443b07-ac8d-495e-a728-90b405cfd1ec)
**Note: üç saat - for 3 hours, saat  üç - since 3 o'clock.**
- Ne zaman*dar beri* buradasınız? Saat dokuz*dan beri* buradayız.
- Ne zama*dar beri* uyuyorsunuz? Saat on iki*den beri* uyuyorum. How long since do you sleep? I'v been sleeping since 12.
- Ne zama*dar beri* hastasınız? Seni son gördüğüm*den berı* hastayim. How long have you been ill. Since last seeing you I have been ill.
  ![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/f75c8302-bb87-4632-96e4-99d6ff82263e)
- Bir hafta*dcr*. For a week.
- Iki yil*dır*. For 2 years
- Dört gündur. For four days
- Uzun bır süredır. For a long time.
- Senı on yıldır tanışıyorum. I've known you for ten years
- Iki saattir parkta yürüyoruz. We've been walking in the park for two hours
---
# ki
[Урок 33. Союз ki и аффикс -ki в турецком языке.](https://www.youtube.com/watch?v=MnHKmpjh6UA&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=34)
## Conjunction:
- Ben biliyorum **ki** sen iyi bir insansın. I know **that** you are a good person.
- Dedim **ki**, "Sana her zaman güvenebilirım".  I said **that** I can always trust you.
- O kadar yoruldum ki! (To express emotions). I'm so tired
- Anladım ki ondan bize fayda yok. I realized that he is of no use to us.
- Anlatın ki anlayalım. Tell us so that we will understand.
## Affix (makes adjective):
- Yarinki toplantı saat 15'te. Tomorrow's meeting is at 15:00
- Sonraki dersimiz ne zaman? When is the next lesson?
**Note: after "gün", "dün", "bugün" ki becomes "kü"
  - Dün**kü** ekmek hâla taze". Yesterdays bread is still fresh.
- Pencerede**kı**" çiçek çok güzel
- Benim arabam senin**ki** kadar hızlı değil. My car is not as fast as **yours one**. (to avoid repetition of words in comparison)
- Ayşe'nin babası yaşlı. Benim**ki** genç.

# Comparison
[Урок 34. Сравнение в турецком языке](https://www.youtube.com/watch?v=wTXpIVuUGVE&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=35)
## Daha - more.
Note: we are using Ablative Case, исходный падеж, dan|den|tan|ten
- Sen ben**den daha** güzelsin. You are more beautiful than me
- O bend**en az** çalışkandır. He is less hardworking than me
- O bend**en daha az** çalışkandır. He is even less hardworking than me. (daha - усиление сравнения).
- Sen bizden daha akıllısın.
- Benim evim senin evinden daha küçük.
## En - most:
Note: two affix izafet
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/81bd4397-762c-4c58-9295-0b2578bdb3bb)

- Bu "en" iyi ev. This is the best house.
- Fransa’nın en güzel şehri Paris’tir.
- O sınıfın en çalışkan öğrencisi. 
---
# Kendi
[Урок 35. Cлово kendi в турецком языке. Свой, сам, себя](https://www.youtube.com/watch?v=olL-_q_jKbM&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=36)
- Kendi araban var ama annenle yaşıyorsun. You have your own car, but you live with your mother. (without possessive pronoun affix)
- Kendi as "self". Ben kendim. Sen kendin. Biz kendimiz. Siz kendiniz.  Onlar kendileri.
   - Saçlarımı **kendım** boyuyorum. I paint my hairs **myself**.
   - Kendine iyi bak. Take care of yourself.
   - Sevgiyı kendimizde bulduk. We found love in ourselves.
   - Kendinizi nasıl hissediyorsunuz. How do you feel about yourself.
   - O kendisine kahve yapıyor. He makes coffee for himself.
   -  Bu videoda kendimizden bahsetmek istiyoruz. We want to talk about ourselves in this video.
---
# Imperatives.
[Урок 36. Повелительное наклонение. Приказ и просьба](https://www.youtube.com/watch?v=vudqR87skI8&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=37)
![image](https://github.com/DmitriiK/Turkish-language/assets/20965831/99b2adda-7e52-4b01-a887-0520bd723f7f)
- Çanta**nız**ı buraya koyun lütfen. Put your bag here, please
- Sen git o bizde kalsın. You go, and he is staying her.
- Sen bekleme. O beklemesin. Siz beklemeyin(yiniz). Onlar beklemesin(lar). Ты не жди. Пусть он на ждет. Вы не ждите. Пусть они не ждут.
- Bir daha bezimle oynama*sın*. Let's they don't play with us.
- Burada sıgara içmeyiniz lütfen
- Sana da ekmek alsın mı? Should he buy bread for you too?
- Aşkımız bitmesin. Let's our love never end.
- Arkadaşın yarın gelsin. Ben onunla görüşmek istiyorum. Let's you friend come tomorrow. I want to see him.
- O başlasın   mı ? Sıra onda. Should he start ? It's his turn.
- Onlar bana telefon etmesınlar.  Kütüphanede konuşmak yasak. Don't let them call me.  It is forbidden to talk in the library
- O saat kaçta seni arasın ? Ne zaman müsaitsin? What time should he call you? When are you free?
- Siz oraya oturun/oturunuz lütfen. Orası boş. Please sit down there. It's empty there.
- Sen sorun çıkarma.  Don't make troubles (Note: ma|me for negativ)
- Sen yalan soyleme. Don't lie.
- Siz  konuşmayın. Don't talk.
  ---
 # Comparison kadar gibi
 [Урок 38. Сравнение при помощи слов kadar и gibi](https://www.youtube.com/watch?v=n-VvCfXj_Tc&list=PLssRXZAfmWU510niYlySaZnOLHwj2jTUP&index=39)

 - Senin araban benim arabam kadar eski. You car is as old as mine

 *Note: личные местоимения становятся притяжательными*
-  O bizim kadar güzel. She is as beautiful as we are
-  Ben onun kadar tembel değilim. I'm not as lazy as he is.
-  
  *Note: Kadar - comparison by quantity. Gibi - for emotional comparison*
-  Sen benım gibi şarkı söylüyorsun. You sing like me
-  Kar gibi beyaz: white as snow. Taş gibi sert: Hard as stone. Buz gibi soğuk: cold as ice.






  













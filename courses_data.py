"""
IPE School mavjud kurslari ro'yxati.
Kurslar:
1. Matematika kids
2. Prezident maktabiga tayyorlov
3. Ixtisoslashgan maktablarga tayyorlov
4. Matematika Abituriyentlar
5. IT Backend
6. IT kids
7. English kids
8. Maktabgacha tayyorlov
9. English
10. CEFR
11. IELTS
12. SAT
"""

COURSES = [
    {
        "key": "math_kids",
        "name": "📐 Matematika kids",
        "description": "Boshlang'ich sinf o'quvchilari uchun mantiqiy fikrlash, hisoblash tezligi va qiziqarli matematika.",
    },
    {
        "key": "pm_prep",
        "name": "🏛 Prezident maktabiga tayyorlov",
        "description": "Prezident maktablarining imtihon standartlari asosida tanqidiy fikrlash (Critical Thinking), muammolarni hal qilish (Problem Solving) va mantiqiy matematika.",
    },
    {
        "key": "spec_prep",
        "name": "🏫 Ixtisoslashgan maktablarga tayyorlov",
        "description": "Al-Xorazmiy, Mirzo Ulug'bek va boshqa yetakchi ixtisoslashtirilgan maktablarga maqsadli kuchaytirilgan tayyorlov kursi.",
    },
    {
        "key": "math_abit",
        "name": "🎓 Matematika Abituriyentlar",
        "description": "Oliy o'quv yurtlari va milliy sertifikat (DTM) imtihonlariga tayyorlanuvchi abituriyentlar uchun chuqurlashtirilgan matematika.",
    },
    {
        "key": "it_backend",
        "name": "⚙️ IT Backend",
        "description": "Python, ma'lumotlar bazasi (SQL), API lar, Telegram botlar va professional backend arxitekturasini o'rganish kursi.",
    },
    {
        "key": "it_kids",
        "name": "💻 IT kids",
        "description": "Bolalar uchun kompyuter savodxonligi, Scratch, algoritmik fikrlash va dasturlashga ilk amaliy qadamlar.",
    },
    {
        "key": "eng_kids",
        "name": "🧒 English kids",
        "description": "Kichik yoshdagi bolalarga ingliz tilini qiziqarli o'yinlar, Speaking va interaktiv mashg'ulotlar orqali o'rgatish.",
    },
    {
        "key": "preschool",
        "name": "🎒 Maktabgacha tayyorlov",
        "description": "5-6 yoshli bolajonlar uchun o'qish, yozish, hisoblash asoslari va maktab muhitiga psixologik tayyorgarlik.",
    },
    {
        "key": "english",
        "name": "🇬🇧 English (General)",
        "description": "Barcha darajalar (Beginner dan Advanced gacha) uchun umumiy ingliz tili: Grammar, Vocabulary, Speaking va Listening.",
    },
    {
        "key": "cefr",
        "name": "📜 CEFR",
        "description": "Milliy va xalqaro CEFR (B1, B2, C1) daraja imtihonlariga maxsus strategik tayyorgarlik kursi.",
    },
    {
        "key": "ielts",
        "name": "🎯 IELTS",
        "description": "IELTS 7.0+ ball olishga yo'naltirilgan intensiv kurs: Listening, Reading, Writing va Speaking bo'limlarini chuqur tahlil qilish.",
    },
    {
        "key": "sat",
        "name": "🇺🇸 SAT",
        "description": "AQSh va xorijiy nufuzli universitetlariga grant asosida kirish uchun SAT Math va Digital SAT tayyorgarligi.",
    },
]


def get_course_by_key(key: str) -> dict | None:
    for course in COURSES:
        if course["key"] == key:
            return course
    return None

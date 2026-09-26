# 🏫 "IPE School" Telegram Payment and Registration Bot

Ushbu bot **IPE School** o'quv markazi uchun ishlab chiqilgan bo'lib, ota-onalarga farzandlarining kurs to'lovlarini (chek yuborish orqali) oson amalga oshirish, maktabning mavjud kurslari bilan tanishish hamda bepul sinov darslariga yozilish imkoniyatini taqdim etadi.

Loyihada **python-telegram-bot v21 (async/await)** arxitekturasidan foydalanilgan.

---

## 📌 Asosiy Xususiyatlar

1. **Majburiy a'zolik (Channel Subscription Check):**
   * Botdan foydalanishdan avval belgilangan rasmiy kanalga obuna tekshiriladi (`get_chat_member`). Obuna bo'lmaguncha bosh menyuga ruxsat berilmaydi.
2. **Asosiy menyu (Inline Menu):**
   * 💳 **To'lov qilish**
   * 📚 **Mavjud kurslar**
   * 🎁 **Bepul darsga yozilish**
   * ℹ️ **Biz haqimizda**
3. **To'lov oqimi (Payment Flow):**
   * Farzandlar sonini tezkor tanlash (1–4 inline tugmalar yoki "5 va undan ko'p" qo'lda son kiritish);
   * Belgilangan songa qarab har bir farzandning ism-familiyasini navbatma-navbat so'rash;
   * To'lov kvitansiyasini (screenshot rasm yoki PDF hujjat) qabul qilish;
   * Ma'lumotlarni tekshirish (preview) va tasdiqlash;
   * Barcha ma'lumotlar va chek `PAYMENTS_CHANNEL_ID` ga yuboriladi.
4. **Bepul darsga yozilish (Free Lesson Flow):**
   * Ota-ona ismi, farzand ismi, yoshi/sinfi, telefon raqami (`+998...` validatsiyasi) va qiziqqan kurs tanlovi;
   * Tasdiqlangach ariza `FREE_LESSON_CHANNEL_ID` ga yuboriladi.
5. **Kurslar katalogi (Courses Catalog):**
   * Kurslar ro'yxati, har bir kursning batafsil dasturi va oylik narxlari.
6. **Xatoliklar va Navigatsiya:**
   * Istalgan vaqtda `/menu` buyrug'i orqali joriy amalni bekor qilib asosiy menyuga qaytish;
   * `/cancel` buyrug'i;
   * 30 daqiqa javob bo'lmasa avtomatik `TIMEOUT` orqali tozalash.

---

## 📂 Loyiha Tuzilishi

```text
payment-ipe-bot/
├── main.py                    # Application yaratish va botni ishga tushirish (polling/webhook)
├── config.py                  # .env dan konfiguratsiyalarni o'qish va tekshirish
├── courses_data.py            # Mavjud kurslar statik ma'lumotlari
├── validators.py              # Ism, telefon, butun son validatsiya funksiyalari
├── keyboards.py               # Barcha inline klaviaturalar
├── caption.py                 # Kanallarga yuboriladigan HTML formatdagi xabarlar
├── handlers/
│   ├── start.py               # /start, kanal obunasi tekshiruvi, asosiy menyu, /menu
│   ├── payment.py             # To'lov oqimi (ConversationHandler)
│   ├── free_lesson.py         # Bepul darsga yozilish oqimi (ConversationHandler)
│   ├── courses.py             # Kurslar katalogi va tafsilotlari
│   ├── about.py               # Biz haqimizda bo'limi
│   └── fallback.py            # /cancel, /menu fallback, timeout va global xatoliklar handleri
├── requirements.txt           # Kerakli kutubxonalar
├── .env.example               # Muhit o'zgaruvchilari namunasi
├── render.yaml                # Render.com Blueprint sozlamalari
├── Procfile                   # Process boshqaruvi
└── README.md                  # Hujjat
```

---

## ⚙️ O'rnatish va Ishga Tushirish

### 1. Loyihani yuklab olish va virtual muhit yaratish
```bash
git clone <repository_url>
cd payment-ipe-bot

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Bog'liqliklarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. `.env` faylini sozlash
`.env.example` faylidan nusxa oling va `.env` nomi bilan saqlang:
```bash
cp .env.example .env
```
Quyidagi qiymatlarni o'zingizning ma'lumotlaringiz bilan to'ldiring:
```env
BOT_TOKEN=123456789:AAA-your-bot-token-here
CHANNEL_ID=@ipe_school_channel
PAYMENTS_CHANNEL_ID=-1001234567890
FREE_LESSON_CHANNEL_ID=-1009876543210

MAX_CHILDREN=10
RUN_MODE=polling
```

> **Muhim eslatma:** Bot `CHANNEL_ID`, `PAYMENTS_CHANNEL_ID` va `FREE_LESSON_CHANNEL_ID` kanallarida **Admin** bo'lishi va xabar yuborish huquqiga ega bo'lishi lozim!

### 4. Botni ishga tushirish
```bash
python main.py
```

---

## ☁️ Render.com ga Joylashtirish (Deployment)

Loyihada Render.com uchun tayyor `render.yaml` mavjud:
1. GitHub reponi Render.com bilan bog'lang (New -> Blueprint).
2. Render avtomatik `render.yaml` faylini aniqlaydi.
3. Render Dashboard'dagi **Environment Variables** bo'limida quyidagi maxfiy o'zgaruvchilarni kiriting:
   * `BOT_TOKEN`
   * `CHANNEL_ID`
   * `PAYMENTS_CHANNEL_ID`
   * `FREE_LESSON_CHANNEL_ID`
4. Deploy tugmasini bosing. Bot fonda Worker sifatida barqaror ishlaydi.

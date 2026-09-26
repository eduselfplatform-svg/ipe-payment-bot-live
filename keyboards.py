from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from courses_data import COURSES
import config


def get_main_reply_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu doimiy pastki Reply klaviaturasi. Adminlar uchun reklama yuborish tugmasi chiqadi."""
    keyboard = [
        [KeyboardButton("💳 To'lov qilish"), KeyboardButton("📚 Mavjud kurslar")],
        [KeyboardButton("🎁 Bepul darsga yozilish"), KeyboardButton("ℹ️ Biz haqimizda")],
    ]
    if is_admin:
        keyboard.append([KeyboardButton("📢 Reklama yuborish")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_welcome_inline_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """
    /start bosilganda rasm ostida chiqadigan inline tugmalar:
    - IPE School kanali
    - Instagram
    - Veb-sayt
    - Kurs uchun to'lov qilish
    """
    keyboard = [
        [
            InlineKeyboardButton("📢 Telegram kanal", url=channel_url),
            InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/ipe_school"),
        ],
        [
            InlineKeyboardButton("🌐 Veb-sayt", url="https://ipeschool.uz/"),
        ],
        [
            InlineKeyboardButton("💳 Kurs uchun to'lov qilish", callback_data="menu_payment"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu inline tugmalari."""
    keyboard = [
        [InlineKeyboardButton("💳 To'lov qilish", callback_data="menu_payment")],
        [InlineKeyboardButton("📚 Mavjud kurslar", callback_data="menu_courses")],
        [InlineKeyboardButton("🎁 Bepul darsga yozilish", callback_data="menu_free_lesson")],
        [InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="menu_about")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Majburiy obuna klaviaturasi: Kanal linki va tasdiqlash tugmasi."""
    keyboard = [
        [InlineKeyboardButton("🔗 Kanalga o'tish", url=channel_url)],
        [InlineKeyboardButton("✅ Men obuna bo'ldim", callback_data="check_subscription")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_child_count_keyboard() -> InlineKeyboardMarkup:
    """Farzandlar sonini tanlash (1-4 va '5 va undan ko'p')."""
    row = [InlineKeyboardButton(str(i), callback_data=f"cc:{i}") for i in range(1, 5)]
    keyboard = [
        row,
        [InlineKeyboardButton("5 va undan ko'p 🔢", callback_data="cc:more")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="pay_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_confirm_keyboard() -> InlineKeyboardMarkup:
    """To'lovni tasdiqlash yoki bekor qilish."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="pay_confirm"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="pay_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_courses_keyboard() -> InlineKeyboardMarkup:
    """Mavjud kurslar katalogi klaviaturasi."""
    keyboard = [
        [InlineKeyboardButton(c["name"], callback_data=f"course:{c['key']}")]
        for c in COURSES
    ]
    keyboard.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)


def get_course_detail_keyboard() -> InlineKeyboardMarkup:
    """Kurs batafsil ko'rilganda orqaga va bepul darsga yozilish tugmalari."""
    keyboard = [
        [InlineKeyboardButton("🎁 Bepul darsga yozilish", callback_data="menu_free_lesson")],
        [InlineKeyboardButton("🔙 Kurslar ro'yxatiga", callback_data="menu_courses")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_free_lesson_courses_keyboard() -> InlineKeyboardMarkup:
    """Bepul dars oqimida kurs tanlash klaviaturasi."""
    keyboard = [
        [InlineKeyboardButton(c["name"], callback_data=f"fl_course:{c['key']}")]
        for c in COURSES
    ]
    keyboard.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="fl_cancel")])
    return InlineKeyboardMarkup(keyboard)


def get_free_lesson_confirm_keyboard() -> InlineKeyboardMarkup:
    """Bepul dars arizasini tasdiqlash yoki bekor qilish."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="fl_confirm"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="fl_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_about_keyboard() -> InlineKeyboardMarkup:
    """Biz haqimizda bo'limi klaviaturasi."""
    keyboard = [
        [InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Har qanday flow ichida oddiy bekor qilish tugmasi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Bekor qilish", callback_data=callback_data)]
    ])


def get_channel_payment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """To'lov kanali uchun admin harakat tugmalari: Tasdiqlash va Bekor qilish."""
    keyboard = [
        [
            InlineKeyboardButton("✅ To'lovni tasdiqlash", callback_data=f"adm_pay:ok:{user_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"adm_pay:rej:{user_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_channel_free_lesson_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Bepul dars kanali uchun boshqaruv tugmalari:
    - Gaplashildi
    - Jarayonda
    - Sinov darsiga qatnashdi
    - Aktiv bo'ldi (ota-onaga bildirishnoma ketadi)
    - Aktiv bo'lmadi
    """
    keyboard = [
        [
            InlineKeyboardButton("📞 Gaplashildi", callback_data=f"adm_fl:called:{user_id}"),
            InlineKeyboardButton("⏳ Jarayonda", callback_data=f"adm_fl:process:{user_id}"),
        ],
        [
            InlineKeyboardButton("🎓 Sinov darsiga qatnashdi", callback_data=f"adm_fl:attended:{user_id}"),
        ],
        [
            InlineKeyboardButton("🟢 Aktiv bo'ldi", callback_data=f"adm_fl:active:{user_id}"),
            InlineKeyboardButton("🔴 Aktiv bo'lmadi", callback_data=f"adm_fl:inactive:{user_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

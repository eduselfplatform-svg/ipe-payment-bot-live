import logging
from telegram import Update
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes
import config
import os
from keyboards import (
    get_main_menu_keyboard,
    get_subscription_keyboard,
    get_main_reply_keyboard,
    get_welcome_inline_keyboard,
)

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "👋 <b>Assalomu alaykum, IPE School rasmiy botiga xush kelibsiz!</b>\n\n"
    "🏫 <b>IPE School</b> — xalqaro ta'lim standartlari, yuqori sifatli darslar va zamonaviy metodikalar "
    "asosida bolalarning intellektual salohiyatini yuksaltiruvchi yetakchi ta'lim maskani.\n\n"
    "📌 <b>Bot orqali siz:</b>\n"
    "• 💳 Farzandingizning kurs to'lovini tez va qulay amalga oshirishingiz,\n"
    "• 📚 Maktabimizning mavjud kurslari bilan batafsil tanishishingiz,\n"
    "• 🎁 Bepul sinov darslariga ro'yxatdan o'tishingiz mumkin.\n\n"
    "Quyidagi tugmalar orqali ijtimoiy tarmoqlarimizga ulanishingiz va kurs uchun to'lov qilishingiz mumkin:"
)


async def is_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """
    Foydalanuvchining majburiy kanalda a'zo ekanligini tekshiradi.
    Bot kanalda admin bo'lishi talab qilinadi.
    """
    try:
        member = await context.bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        return False
    except Exception as e:
        logger.warning(f"Obunani tekshirishda xatolik ({config.CHANNEL_ID}, user_id={user_id}): {e}")
        return True


def get_channel_link() -> str:
    """Kanal havolasini tayyorlash."""
    ch = str(config.CHANNEL_ID)
    if ch.startswith("@"):
        return f"https://t.me/{ch[1:]}"
    elif ch.startswith("https://t.me/"):
        return ch
    return "https://t.me/"


# Bir marta yuborilgan rasmning Telegram file_id sini keshlab olamiz (qayta-qayta fayl yuklanmasligi uchun tez ishlaydi)
CACHED_WELCOME_PHOTO_FILE_ID: str | None = None


def get_welcome_image_path() -> str | None:
    """Rasmni loyiha ichidan eng yaqin va optimallashgan variantini topadi."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "welcome.jpg"),
        os.path.join(base_dir, "image.png"),
        os.path.join(os.getcwd(), "welcome.jpg"),
        os.path.join(os.getcwd(), "image.png"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start bosilganda yoki obuna tasdiqlanganda:
    Rasmni Telegram file_id keshi orqali zumda yuboradi,
    inline tugmalar va pastki Reply menyuni chiqaradi.
    """
    global CACHED_WELCOME_PHOTO_FILE_ID
    chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    user_id = update.effective_user.id if update.effective_user else 0
    channel_url = get_channel_link()
    inline_kb = get_welcome_inline_keyboard(channel_url)
    
    is_user_admin = user_id in config.ADMIN_IDS
    reply_kb = get_main_reply_keyboard(is_admin=is_user_admin)

    photo_sent = False

    # 1. Agar avval file_id olingan bo'lsa, faylni qayta yuklamasdan file_id bilan soniyada yuboramiz
    if CACHED_WELCOME_PHOTO_FILE_ID:
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=CACHED_WELCOME_PHOTO_FILE_ID,
                caption=WELCOME_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=inline_kb,
            )
            photo_sent = True
        except Exception as e:
            logger.warning(f"Keshdagi file_id bilan rasm yuborilmadi, fayldan o'qiladi: {e}")
            CACHED_WELCOME_PHOTO_FILE_ID = None

    # 2. Agar keshda bo'lmasa, lokal fayldan ochib yuboramiz va file_id sini saqlaymiz
    if not photo_sent:
        img_path = get_welcome_image_path()
        if img_path:
            try:
                with open(img_path, "rb") as f:
                    msg = await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=f,
                        caption=WELCOME_TEXT,
                        parse_mode=ParseMode.HTML,
                        reply_markup=inline_kb,
                    )
                    # Keyingi barcha foydalanuvchilar uchun 1 ms da ketishi uchun file_id ni saqlaymiz
                    if msg.photo:
                        CACHED_WELCOME_PHOTO_FILE_ID = msg.photo[-1].file_id
                    photo_sent = True
            except Exception as e:
                logger.error(f"Rasmni yuborishda xatolik yuz berdi: {e}")

    # 3. Agar rasm umuman topilmasa yoki yuborilmasa, xabarni matn ko'rinishida yuboramiz
    if not photo_sent:
        await context.bot.send_message(
            chat_id=chat_id,
            text=WELCOME_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_kb,
        )

    # Pastki reply keyboard menyuni ham ta'minlaymiz
    await context.bot.send_message(
        chat_id=chat_id,
        text="👇 Kerakli bo'limni quyidagi menyudan ham tanlashingiz mumkin:",
        reply_markup=reply_kb,
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit_message: bool = False):
    """Asosiy menyuni ko'rsatish (ichki sahifalardan qaytganda)."""
    channel_url = get_channel_link()
    inline_markup = get_welcome_inline_keyboard(channel_url)
    user_id = update.effective_user.id if update.effective_user else 0
    is_user_admin = user_id in config.ADMIN_IDS
    reply_markup = get_main_reply_keyboard(is_admin=is_user_admin)

    if edit_message and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=WELCOME_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=inline_markup,
            )
            return
        except Exception:
            pass

    target_chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    await context.bot.send_message(
        chat_id=target_chat_id,
        text=WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


import storage


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start buyrug'i: Avval kanalga obuna tekshiriladi, obuna bo'lsa rasm + tanishtiruv chiqadi.
    """
    if update.effective_chat:
        storage.save_user(update.effective_chat.id)

    user = update.effective_user
    subscribed = await is_subscribed(context, user.id)

    if not subscribed:
        channel_url = get_channel_link()
        text = (
            f"👋 Assalomu alaykum, <b>{user.first_name}</b>!\n\n"
            "Botdan to'liq foydalanish va to'lovlarni amalga oshirish uchun avval bizning rasmiy kanalimizga a'zo bo'ling."
        )
        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_subscription_keyboard(channel_url)
        )
        return

    await send_welcome_message(update, context)


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'✅ Men obuna bo'ldim' tugmasi bosilganda qayta tekshirish."""
    query = update.callback_query
    await query.answer()

    if update.effective_chat:
        storage.save_user(update.effective_chat.id)

    user = update.effective_user
    subscribed = await is_subscribed(context, user.id)

    if not subscribed:
        await query.answer("❗️ Siz hali kanalga a'zo bo'lmadingiz. Iltimos, avval obuna bo'ling!", show_alert=True)
        return

    await query.message.delete()
    await send_welcome_message(update, context)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/menu buyrug'i: Har qanday vaqtda asosiy menyuga qaytaradi."""
    context.user_data.clear()
    await show_main_menu(update, context, edit_message=False)


async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline '🔙 Bosh menyu' tugmasi bosilganda."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await show_main_menu(update, context, edit_message=True)

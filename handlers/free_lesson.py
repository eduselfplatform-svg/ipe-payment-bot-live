import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)

import config
from caption import format_free_lesson_message
from courses_data import get_course_by_key
from keyboards import (
    get_free_lesson_courses_keyboard,
    get_free_lesson_confirm_keyboard,
    get_cancel_keyboard,
)
from validators import validate_not_empty, validate_phone
from handlers.fallback import cancel_command, menu_fallback, timeout_handler

logger = logging.getLogger(__name__)

# Holatlar (States)
PARENT_NAME, CHILD_NAME_FL, CHILD_AGE, PHONE, COURSE_CHOICE, CONFIRM_FL = range(6)


async def start_free_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Bepul darsga yozilish oqimi boshlanishi: Ota-onaning ism-familiyasi so'raladi.
    """
    if update.callback_query:
        await update.callback_query.answer()

    context.user_data.clear()

    text = (
        "🎁 <b>Bepul sinov darsiga yozilish</b>\n\n"
        "Farzandingiz uchun bepul sinov darsiga qatnashish arizasini to'ldirishga xush kelibsiz!\n\n"
        "1️⃣ <b>Ota-onaning ism va familiyasini</b> kiriting:"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_cancel_keyboard("fl_cancel"),
        )
    else:
        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_cancel_keyboard("fl_cancel"),
        )
    return PARENT_NAME


async def handle_parent_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ota-onaning ism-familiyasini tekshirish va qabul qilish."""
    text = update.message.text
    is_valid, result = validate_not_empty(text, min_len=3, max_len=100)

    if not is_valid:
        await update.message.reply_text(
            text=result,
            reply_markup=get_cancel_keyboard("fl_cancel"),
        )
        return PARENT_NAME

    context.user_data["parent_name"] = result

    await update.message.reply_text(
        text=(
            "2️⃣ <b>Farzandingizning ism va familiyasini</b> kiriting:"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard("fl_cancel"),
    )
    return CHILD_NAME_FL


async def handle_child_name_fl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Farzandning ism-familiyasini tekshirish va qabul qilish."""
    text = update.message.text
    is_valid, result = validate_not_empty(text, min_len=3, max_len=100)

    if not is_valid:
        await update.message.reply_text(
            text=result,
            reply_markup=get_cancel_keyboard("fl_cancel"),
        )
        return CHILD_NAME_FL

    context.user_data["child_name"] = result

    await update.message.reply_text(
        text=(
            "3️⃣ <b>Farzandingizning yoshi yoki sinfini</b> kiriting\n"
            "<i>(Masalan: 10 yosh yoki 4-sinf):</i>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard("fl_cancel"),
    )
    return CHILD_AGE


async def handle_child_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Farzandning yoshi yoki sinfini tekshirish va qabul qilish."""
    text = update.message.text
    is_valid, result = validate_not_empty(text, min_len=1, max_len=50)

    if not is_valid:
        await update.message.reply_text(
            text=result,
            reply_markup=get_cancel_keyboard("fl_cancel"),
        )
        return CHILD_AGE

    context.user_data["child_age"] = result

    await update.message.reply_text(
        text=(
            "4️⃣ Bog'lanish uchun <b>telefon raqamingizni</b> kiriting:\n"
            "<i>(Misol: +998901234567)</i>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard("fl_cancel"),
    )
    return PHONE


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Telefon raqamini tekshirish va qabul qilish."""
    text = update.message.text
    is_valid, result = validate_phone(text)

    if not is_valid:
        await update.message.reply_text(
            text=result,
            reply_markup=get_cancel_keyboard("fl_cancel"),
        )
        return PHONE

    context.user_data["phone"] = result

    await update.message.reply_text(
        text=(
            "5️⃣ Farzandingiz <b>qaysi kursga qiziqmoqda?</b>\n"
            "Quyidagi kurslardan birini tanlang:"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=get_free_lesson_courses_keyboard(),
    )
    return COURSE_CHOICE


async def handle_course_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Kurs tanlanganda uni saqlash va tekshirish (Preview) chiqarish."""
    query = update.callback_query
    await query.answer()

    key = query.data.split(":")[1]
    course = get_course_by_key(key)
    course_name = course["name"] if course else key

    context.user_data["interested_course"] = course_name

    # Preview xabari
    user_data = context.user_data
    text = (
        "🔎 <b>Arizani tekshiring:</b>\n\n"
        f"👤 <b>Ota-ona:</b> {user_data.get('parent_name')}\n"
        f"👶 <b>Farzand:</b> {user_data.get('child_name')} ({user_data.get('child_age')})\n"
        f"📞 <b>Telefon:</b> {user_data.get('phone')}\n"
        f"📚 <b>Kurs:</b> {user_data.get('interested_course')}\n\n"
        "Barcha ma'lumotlar to'g'rimi?"
    )

    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_free_lesson_confirm_keyboard(),
    )
    return CONFIRM_FL


async def handle_free_lesson_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Tasdiqlash bosilganda FREE_LESSON_CHANNEL_ID ga yuborish."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "fl_cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ Sinov darsiga yozilish bekor qilindi.")
        from handlers.start import show_main_menu
        await show_main_menu(update, context, edit_message=False)
        return ConversationHandler.END

    user = update.effective_user
    user_data = context.user_data
    channel_msg = format_free_lesson_message(user, user_data)

    from keyboards import get_channel_free_lesson_keyboard
    channel_kb = get_channel_free_lesson_keyboard(user.id)

    try:
        await context.bot.send_message(
            chat_id=config.FREE_LESSON_CHANNEL_ID,
            text=channel_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=channel_kb,
        )
        await query.edit_message_text(
            text=(
                "✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
                "Tez orada o'quv bo'limi ma'muri siz bilan bog'lanib, bepul sinov darsi kuni va "
                "vaqtini belgilaydi. Rahmat!"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.exception(f"Bepul dars arizasini kanalga yuborishda xatolik: {e}")
        await query.edit_message_text(
            text=(
                "✅ <b>Arizangiz qabul qilindi!</b>\n\n"
                "Ma'lumotlar ro'yxatga olindi. Ma'murimiz tez orada siz bilan bog'lanadi."
            ),
            parse_mode=ParseMode.HTML,
        )

    context.user_data.clear()
    from handlers.start import show_main_menu
    await show_main_menu(update, context, edit_message=False)
    return ConversationHandler.END


free_lesson_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_free_lesson, pattern="^menu_free_lesson$"),
        MessageHandler(filters.Regex("^🎁 Bepul darsga yozilish$"), start_free_lesson),
    ],
    states={
        PARENT_NAME: [
            CallbackQueryHandler(handle_free_lesson_confirm, pattern="^fl_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_parent_name),
        ],
        CHILD_NAME_FL: [
            CallbackQueryHandler(handle_free_lesson_confirm, pattern="^fl_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_child_name_fl),
        ],
        CHILD_AGE: [
            CallbackQueryHandler(handle_free_lesson_confirm, pattern="^fl_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_child_age),
        ],
        PHONE: [
            CallbackQueryHandler(handle_free_lesson_confirm, pattern="^fl_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone),
        ],
        COURSE_CHOICE: [
            CallbackQueryHandler(handle_free_lesson_confirm, pattern="^fl_cancel$"),
            CallbackQueryHandler(handle_course_choice, pattern=r"^fl_course:"),
        ],
        CONFIRM_FL: [
            CallbackQueryHandler(handle_free_lesson_confirm, pattern="^fl_(confirm|cancel)$"),
        ],
        ConversationHandler.TIMEOUT: [
            MessageHandler(filters.ALL, timeout_handler),
            CallbackQueryHandler(timeout_handler),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_command),
        CommandHandler("menu", menu_fallback),
        CallbackQueryHandler(cancel_command, pattern="^fl_cancel$"),
    ],
    conversation_timeout=config.CONVERSATION_TIMEOUT_SECONDS,
    name="free_lesson_conversation",
)

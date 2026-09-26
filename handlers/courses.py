from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from courses_data import COURSES, get_course_by_key
from keyboards import get_courses_keyboard, get_course_detail_keyboard


async def show_courses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mavjud kurslar ro'yxatini inline klaviatura bilan ko'rsatish."""
    query = update.callback_query
    if query:
        await query.answer()

    text = (
        "📚 <b>IPE School mavjud kurslari</b>\n\n"
        "Quyidagi kurslardan birini tanlab, darslar haqida batafsil ma'lumot "
        "va oylik to'lov narxlarini bilib olishingiz mumkin:"
    )

    if query and query.message:
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_courses_keyboard(),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_courses_keyboard(),
        )


async def show_course_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tanlangan kurs bo'yicha batafsil ma'lumotni chiqarish."""
    query = update.callback_query
    await query.answer()

    key = query.data.split(":")[1]
    course = get_course_by_key(key)

    if not course:
        await query.edit_message_text("Kechirasiz, ushbu kurs haqida ma'lumot topilmadi.")
        return

    text = (
        f"<b>{course['name']}</b>\n\n"
        f"{course['description']}\n\n"
        "ℹ️ <i>Kurslar dasturi, dars jadvali va to'lov narxlari bo'yicha batafsil ma'lumot "
        "bepul sinov darsiga yozilganingizda adminlarimiz tomonidan to'liq tushuntirib beriladi.</i>"
    )

    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_course_detail_keyboard(),
    )

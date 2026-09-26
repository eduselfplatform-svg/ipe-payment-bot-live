from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from keyboards import get_about_keyboard

ABOUT_TEXT = (
    "ℹ️ <b>IPE School haqida</b>\n\n"
    "🏫 <b>IPE School</b> — zamonaviy ta'lim standartlari, malakali ustozlar jamoasi "
    "va ilg'or xorijiy metodikalar asosida yoshlarning intellektual salohiyatini "
    "rivojlantiruvchi yetakchi innovatsion ta'lim markazidir.\n\n"
    "🎯 <b>Bizning maqsadimiz:</b> har bir o'quvchida mustaqil fikrlash, kuchli mantiq "
    "va kelajak kasblari uchun zarur bo'lgan mustahkam bilimlarni shakllantirish.\n\n"
    "💡 <b>Loyiha haqida:</b>\n"
    "Ushbu Telegram bot to'liq <b>IPE School o'quvchilarining bilimi va mashaqqatli mehnati</b> "
    "evaziga ishlab chiqilgan va amaliyotga tatbiq etilgan!\n\n"
    "👨‍💻 <b>Loyihada ishlagan iqtidorli o'quvchilar:</b>\n"
    "• Muxriddin\n"
    "• Miraziz\n"
    "• Qobiljon\n"
    "• Behruz\n"
    "• Husan\n"
    "• Ismatilla\n\n"
    "📩 <b>Aloqa va qo'llab-quvvatlash:</b> @Ipeschool44\n"
    "📞 <b>Telefon:</b> +998 55 588 50 00\n"
    "📞 <b>Qo'shimcha tel:</b> +998 71 295 11 05"
)


async def show_about_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'Biz haqimizda' bo'limi ma'lumotlarini ko'rsatish."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text=ABOUT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_about_keyboard(),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ABOUT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=get_about_keyboard(),
        )

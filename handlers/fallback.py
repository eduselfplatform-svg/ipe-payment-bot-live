import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    /cancel buyrug'i bosilganda joriy jarayon bekor qilinadi va asosiy menyu ko'rsatiladi.
    """
    context.user_data.clear()
    msg = (
        "❌ <b>Jarayon bekor qilindi.</b>\n\n"
        "Asosiy menyuga qaytdingiz. Kerakli bo'limni tanlashingiz mumkin:"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=msg,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard(),
        )
    elif update.message:
        await update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard(),
        )
    return ConversationHandler.END


async def menu_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Har qanday flow davomida /menu bosilsa, joriy jarayon tugatilib, menyu ochiladi.
    """
    context.user_data.clear()
    from handlers.start import show_main_menu
    await show_main_menu(update, context, edit_message=False)
    return ConversationHandler.END


async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    ConversationHandler timeout (30 daqiqa) bo'lganda avtomatik ishga tushadi.
    """
    context.user_data.clear()
    chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "⏳ <b>Javobsizlik sababli jarayon yakunlandi.</b>\n\n"
                "Qaytadan boshlash uchun /menu yoki /start buyrug'ini yuboring."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard(),
        )
    except Exception as e:
        logger.warning(f"Timeout xabarini yuborishda xatolik: {e}")
    return ConversationHandler.END


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Kutilmagan xatoliklarni xavfsiz ushlab qolish va loglash.
    """
    logger.exception("Kutilmagan xatolik yuz berdi:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring yoki /menu orqali bosh menyuga o'ting.",
            )
        except Exception:
            pass

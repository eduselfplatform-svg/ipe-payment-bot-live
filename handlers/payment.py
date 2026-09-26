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
from caption import format_payment_caption
from keyboards import (
    get_child_count_keyboard,
    get_payment_confirm_keyboard,
    get_cancel_keyboard,
    get_subscription_keyboard,
)
from validators import validate_not_empty, validate_int
from handlers.fallback import cancel_command, menu_fallback, timeout_handler

logger = logging.getLogger(__name__)

# Holatlar (States)
CHILD_COUNT, CHILD_COUNT_MANUAL, CHILD_NAME, RECEIPT, CONFIRM = range(5)


async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    To'lov oqimining boshlanishi. Farzandlar sonini tanlash so'raladi.
    DIQQAT: To'lov qilish uchun kanalga obuna majburiy!
    """
    if update.callback_query:
        await update.callback_query.answer()

    user = update.effective_user
    from handlers.start import is_subscribed, get_channel_link
    subscribed = await is_subscribed(context, user.id)

    if not subscribed:
        channel_url = get_channel_link()
        text = (
            "❗️ <b>To'lovni amalga oshirish uchun avval kanalimizga a'zo bo'lishingiz shart.</b>\n\n"
            "Iltimos, quyidagi tugma orqali kanalga obuna bo'ling va keyin to'lovni davom ettiring:"
        )
        sub_kb = get_subscription_keyboard(channel_url)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=sub_kb,
            )
        else:
            await update.message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=sub_kb,
            )
        return ConversationHandler.END

    # Ma'lumotlarni tozalash va tayyorlash
    context.user_data.clear()
    context.user_data["children_names"] = []
    context.user_data["_child_index"] = 0

    text = (
        "💳 <b>Kurs to'lovini amalga oshirish</b>\n\n"
        "Nechta farzandingiz uchun to'lov qilmoqchisiz?\n"
        "Quyidagi tugmalardan birini tanlang:"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_child_count_keyboard(),
        )
    else:
        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_child_count_keyboard(),
        )
    return CHILD_COUNT


async def handle_child_count_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Farzandlar soni inline tugmasi bosilganda:
    - cc:1..4 bo'lsa to'g'ridan-to'g'ri CHILD_NAME ga o'tadi
    - cc:more bo'lsa CHILD_COUNT_MANUAL ga o'tadi
    """
    query = update.callback_query
    await query.answer()

    data = query.data  # Masalan: cc:2 yoki cc:more

    if data == "cc:more":
        await query.edit_message_text(
            text=(
                "🔢 <b>Farzandlar sonini kiriting:</b>\n\n"
                f"Nechta farzand uchun to'lov qilyapsiz? (1 dan {config.MAX_CHILDREN} gacha son yozing):"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_cancel_keyboard("pay_cancel"),
        )
        return CHILD_COUNT_MANUAL

    count = int(data.split(":")[1])
    context.user_data["child_count"] = count
    context.user_data["_child_index"] = 0
    context.user_data["children_names"] = []

    await query.edit_message_text(
        text=(
            f"✅ <b>{count} nafar farzand</b> tanlandi.\n\n"
            f"👶 1-farzandingizning ism va familiyasini kiriting (1/{count}):"
        ),
        parse_mode=ParseMode.HTML,
    )
    return CHILD_NAME


async def handle_child_count_manual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Foydalanuvchi sonni qo'lda matn sifatida kiritganda validatsiya.
    """
    text = update.message.text
    is_valid, result = validate_int(text, min_v=1, max_v=config.MAX_CHILDREN)

    if not is_valid:
        await update.message.reply_text(
            text=str(result),
            reply_markup=get_cancel_keyboard("pay_cancel"),
        )
        return CHILD_COUNT_MANUAL

    count = int(result)
    context.user_data["child_count"] = count
    context.user_data["_child_index"] = 0
    context.user_data["children_names"] = []

    await update.message.reply_text(
        text=(
            f"✅ <b>{count} nafar farzand</b> kiritildi.\n\n"
            f"👶 1-farzandingizning ism va familiyasini kiriting (1/{count}):"
        ),
        parse_mode=ParseMode.HTML,
    )
    return CHILD_NAME


async def ask_next_child_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Navbatdagi farzand ismini so'rash yordamchisi."""
    idx = context.user_data["_child_index"]
    total = context.user_data["child_count"]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"👶 <b>{idx + 1}-farzandning</b> ism va familiyasini kiriting ({idx + 1}/{total}):",
        parse_mode=ParseMode.HTML,
    )


async def handle_child_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Farzand ism-familiyasini qabul qilish va tekshirish (tsikl).
    """
    text = update.message.text
    is_valid, result = validate_not_empty(text, min_len=3, max_len=80)

    if not is_valid:
        await update.message.reply_text(
            text=result,
            reply_markup=get_cancel_keyboard("pay_cancel"),
        )
        return CHILD_NAME

    context.user_data["children_names"].append(result)
    context.user_data["_child_index"] += 1

    total = context.user_data["child_count"]
    current_idx = context.user_data["_child_index"]

    if current_idx < total:
        await ask_next_child_name(update, context)
        return CHILD_NAME

    # Barcha ismlar qabul qilindi -> Chek so'raladi
    await update.message.reply_text(
        text=(
            "💵 <b>To'lov chekini yuboring:</b>\n\n"
            "To'lov kvitansiyasini rasm (screenshot) yoki PDF hujjat shaklida yuboring.\n\n"
            "❗️ <i>Chekda to'lov summasi, sana va to'lovchi ismi aniq ko'rinishi kerak.</i>"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard("pay_cancel"),
    )
    return RECEIPT


async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    To'lov chekini qabul qilish (Photo yoki PDF Document).
    """
    message = update.message

    if message.photo:
        context.user_data["receipt_type"] = "photo"
        context.user_data["receipt_file_id"] = message.photo[-1].file_id
    elif message.document and message.document.mime_type == "application/pdf":
        context.user_data["receipt_type"] = "document"
        context.user_data["receipt_file_id"] = message.document.file_id
    else:
        await message.reply_text(
            text=(
                "❗️ <b>Noto'g'ri fayl formati!</b>\n\n"
                "Iltimos, chekni rasm (screenshot) yoki PDF fayl ko'rinishida yuboring."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_cancel_keyboard("pay_cancel"),
        )
        return RECEIPT

    await show_payment_confirmation(update, context)
    return CONFIRM


async def handle_invalid_receipt_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Agar rasm yoki PDF o'rniga matn yoki boshqa fayl yuborilsa."""
    await update.message.reply_text(
        text=(
            "❗️ Iltimos, to'lov chekini rasm (screenshot) yoki PDF fayl sifatida yuboring."
        ),
        reply_markup=get_cancel_keyboard("pay_cancel"),
    )
    return RECEIPT


async def show_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Yakuniy tasdiqlash xabari (Preview).
    """
    names = "\n".join(f"  {i + 1}. {n}" for i, n in enumerate(context.user_data["children_names"]))
    text = (
        "🔎 <b>To'lov ma'lumotlarini tekshiring:</b>\n\n"
        f"👶 <b>Farzandlar soni:</b> {context.user_data['child_count']}\n"
        f"📋 <b>Ismlari:</b>\n{names}\n\n"
        "📎 To'lov cheki qabul qilindi.\n\n"
        "Barcha ma'lumotlar to'g'rimi?"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_payment_confirm_keyboard(),
    )


async def handle_payment_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Tasdiqlash bosilganda PAYMENTS_CHANNEL_ID ga yuborish, bekor qilinsa tozalash.
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "pay_cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ To'lov arizasi bekor qilindi.")
        from handlers.start import show_main_menu
        await show_main_menu(update, context, edit_message=False)
        return ConversationHandler.END

    # Tasdiqlanganda kanalga yuborish
    user = update.effective_user
    user_data = context.user_data
    caption = format_payment_caption(user, user_data)

    from keyboards import get_channel_payment_keyboard
    channel_kb = get_channel_payment_keyboard(user.id)

    try:
        if user_data.get("receipt_type") == "photo":
            await context.bot.send_photo(
                chat_id=config.PAYMENTS_CHANNEL_ID,
                photo=user_data["receipt_file_id"],
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=channel_kb,
            )
        else:
            await context.bot.send_document(
                chat_id=config.PAYMENTS_CHANNEL_ID,
                document=user_data["receipt_file_id"],
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=channel_kb,
            )

        await query.edit_message_text(
            text=(
                "✅ <b>To'lovingiz qabul qilindi!</b>\n\n"
                "To'lov chekingiz ma'muriyatga yuborildi. Tez orada tekshirilib tasdiqlanadi. "
                "IPE School'ni tanlaganingiz uchun tashakkur!"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.exception(f"To'lov ma'lumotini kanalga yuborishda xatolik: {e}")
        await query.edit_message_text(
            text=(
                "✅ <b>To'lov cheki qabul qilindi!</b>\n\n"
                "Ma'lumotlar ro'yxatga olindi. Operatorlarimiz tez orada siz bilan bog'lanishadi."
            ),
            parse_mode=ParseMode.HTML,
        )

    context.user_data.clear()
    from handlers.start import show_main_menu
    await show_main_menu(update, context, edit_message=False)
    return ConversationHandler.END


payment_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_payment, pattern="^menu_payment$"),
        MessageHandler(filters.Regex("^💳 To'lov qilish$"), start_payment),
    ],
    states={
        CHILD_COUNT: [
            CallbackQueryHandler(handle_payment_confirm, pattern="^pay_cancel$"),
            CallbackQueryHandler(handle_child_count_choice, pattern=r"^cc:"),
        ],
        CHILD_COUNT_MANUAL: [
            CallbackQueryHandler(handle_payment_confirm, pattern="^pay_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_child_count_manual),
        ],
        CHILD_NAME: [
            CallbackQueryHandler(handle_payment_confirm, pattern="^pay_cancel$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_child_name),
        ],
        RECEIPT: [
            CallbackQueryHandler(handle_payment_confirm, pattern="^pay_cancel$"),
            MessageHandler(filters.PHOTO | (filters.Document.ALL & filters.Document.PDF), handle_receipt),
            MessageHandler(filters.ALL & ~filters.COMMAND, handle_invalid_receipt_format),
        ],
        CONFIRM: [
            CallbackQueryHandler(handle_payment_confirm, pattern="^pay_(confirm|cancel)$"),
        ],
        ConversationHandler.TIMEOUT: [
            MessageHandler(filters.ALL, timeout_handler),
            CallbackQueryHandler(timeout_handler),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_command),
        CommandHandler("menu", menu_fallback),
        CallbackQueryHandler(cancel_command, pattern="^pay_cancel$"),
    ],
    conversation_timeout=config.CONVERSATION_TIMEOUT_SECONDS,
    name="payment_conversation",
)

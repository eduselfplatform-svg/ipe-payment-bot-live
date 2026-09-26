import asyncio
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import config
import storage
from handlers.fallback import cancel_command

logger = logging.getLogger(__name__)

ASK_CONTENT, CONFIRM = range(2)


async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    /broadcast buyrug'i faqat config.ADMIN_IDS dagi adminlar uchun ishlaydi.
    """
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        return ConversationHandler.END

    all_users = storage.get_all_user_ids()
    await update.message.reply_text(
        f"📢 <b>Reklama yuborish (Broadcast)</b>\n\n"
        f"👥 Baza foydalanuvchilari soni: <b>{len(all_users)}</b> ta.\n\n"
        "Iltimos, reklama uchun xabarni yuboring (rasm+matn, video+matn yoki shunchaki matn):\n\n"
        "<i>Bekor qilish uchun /cancel yozing.</i>",
        parse_mode=ParseMode.HTML,
    )
    return ASK_CONTENT


async def broadcast_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Admin yuborgan kontentni qabul qilib oladi va o'ziga Preview ko'rsatadi.
    """
    msg = update.message
    context.user_data["broadcast"] = {
        "text": msg.text or msg.caption or "",
        "photo": msg.photo[-1].file_id if msg.photo else None,
        "video": msg.video.file_id if msg.video else None,
    }

    # O'ziga preview ko'rsatish
    await msg.copy(chat_id=msg.chat_id)

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yuborish", callback_data="bc_send"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="bc_cancel"),
        ]
    ])

    await update.message.reply_text(
        "👆 <b>Xabar ko'rinishi yuqoridagi kabi bo'ladi.</b>\n\n"
        "Ushbu xabar barcha foydalanuvchilarga tarqatilsinmi?",
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )
    return CONFIRM


async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Admin tasdiqlasa, barcha foydalanuvchilarga tarqatiladi va hisobot beriladi.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "bc_cancel":
        context.user_data.pop("broadcast", None)
        await query.edit_message_text("❌ Reklama yuborish bekor qilindi.")
        return ConversationHandler.END

    data = context.user_data.get("broadcast")
    if not data:
        await query.edit_message_text("❌ Xatolik: Xabar ma'lumotlari topilmadi.")
        return ConversationHandler.END

    user_ids = storage.get_all_user_ids()
    total = len(user_ids)

    if total == 0:
        await query.edit_message_text("⚠️ Bazada hali foydalanuvchilar mavjud emas.")
        return ConversationHandler.END

    await query.edit_message_text(f"🚀 Reklama {total} ta foydalanuvchiga yuborilmoqda, iltimos kuting...")

    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            if data["photo"]:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=data["photo"],
                    caption=data["text"],
                    parse_mode=ParseMode.HTML if data["text"] else None,
                )
            elif data["video"]:
                await context.bot.send_video(
                    chat_id=uid,
                    video=data["video"],
                    caption=data["text"],
                    parse_mode=ParseMode.HTML if data["text"] else None,
                )
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=data["text"],
                    parse_mode=ParseMode.HTML,
                )
            sent += 1
        except Exception as e:
            failed += 1
            logger.info(f"Foydalanuvchiga xabar yuborilmadi ({uid}): {e}")
            # Agar bot bloklangan bo'lsa (Forbidden: bot was blocked by the user) bazadan olib tashlash mumkin
            if "blocked by the user" in str(e).lower() or "chat not found" in str(e).lower():
                storage.remove_user(uid)

        # Telegram flood limitdan saqlanish
        await asyncio.sleep(0.05)

    context.user_data.pop("broadcast", None)
    await query.message.reply_text(
        f"✅ <b>Reklama muvaffaqiyatli yakunlandi!</b>\n\n"
        f"📨 Yuborildi: <b>{sent}</b> ta foydalanuvchiga\n"
        f"⚠️ Yuborilmadi (bloklangan/o'chirilgan): <b>{failed}</b> ta",
        parse_mode=ParseMode.HTML,
    )
    return ConversationHandler.END


broadcast_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("broadcast", broadcast_start),
        MessageHandler(filters.Regex("^📢 Reklama yuborish$"), broadcast_start),
    ],
    states={
        ASK_CONTENT: [
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT & ~filters.COMMAND, broadcast_receive)
        ],
        CONFIRM: [
            CallbackQueryHandler(broadcast_confirm, pattern="^bc_")
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_command)],
    conversation_timeout=config.CONVERSATION_TIMEOUT_SECONDS,
    name="broadcast_conversation",
)

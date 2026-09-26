import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes
import config

logger = logging.getLogger(__name__)


async def is_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int | str) -> bool:
    """
    Tugmani bosgan shaxs admin ekanligini tekshiradi:
    1. config.ADMIN_IDS ro'yxatida bo'lsa -> True
    2. Kanal yoki guruhda (chat_id) administrator/creator bo'lsa -> True
    3. Aks holda -> False
    """
    if config.ADMIN_IDS and user_id in config.ADMIN_IDS:
        return True

    try:
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
    except Exception as e:
        logger.warning(f"Admin huquqini tekshirishda xatolik (chat={chat_id}, user={user_id}): {e}")

    # Agar ADMIN_IDS berilmagan bo'lsa va tekshirib bo'lmasa, faqat chat admins
    return False


async def handle_channel_payment_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    To'lov kanalidagi "✅ To'lovni tasdiqlash" va "❌ Rad etish" tugmalarini qayta ishlash.
    Callback data: adm_pay:<action>:<user_id>
    """
    query = update.callback_query
    admin_user = query.from_user
    chat = query.message.chat

    # Faqat adminlar bosishi mumkin
    if not await is_admin(context, admin_user.id, chat.id):
        await query.answer("⛔️ Bu tugmani faqat kanal administratorlari boshqara oladi!", show_alert=True)
        return

    parts = query.data.split(":")
    action = parts[1]  # "ok" yoki "rej"
    parent_id = int(parts[2])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    admin_name = admin_user.full_name

    current_caption = query.message.caption or query.message.text or ""

    if action == "ok":
        # 1. Kanal xabariga status qo'shish
        status_text = f"\n\n━━━━━━━━━━━━━━━━━━━━\n✅ <b>TO'LOV TASDIQLANDI</b>\n👨‍💼 Mas'ul: {admin_name}\n🕒 Vaqt: {now_str}"
        new_caption = current_caption + status_text

        try:
            if query.message.photo or query.message.document:
                await query.edit_message_caption(caption=new_caption, parse_mode=ParseMode.HTML, reply_markup=None)
            else:
                await query.edit_message_text(text=new_caption, parse_mode=ParseMode.HTML, reply_markup=None)
        except Exception as e:
            logger.warning(f"Kanal xabarini tahrirlashda xatolik: {e}")

        # 2. Ota-onaga bildirishnoma yuborish
        try:
            await context.bot.send_message(
                chat_id=parent_id,
                text=(
                    "🎉 <b>Xushxabar! Sizning to'lovingiz tasdiqlandi.</b>\n\n"
                    "Farzandingizning darslari muvaffaqiyatli faollashtirildi. "
                    "IPE School jamoasi sizga minnatdorchilik bildiradi! 📚✨"
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.warning(f"Ota-onaga bildirishnoma yuborilmadi (user_id={parent_id}): {e}")

        await query.answer("✅ To'lov tasdiqlandi va ota-onaga xabar yuborildi.")

    elif action == "rej":
        # 1. Kanal xabariga status qo'shish
        status_text = f"\n\n━━━━━━━━━━━━━━━━━━━━\n❌ <b>TO'LOV RAD ETILDI / KAMCHILIK BOR</b>\n👨‍💼 Mas'ul: {admin_name}\n🕒 Vaqt: {now_str}"
        new_caption = current_caption + status_text

        try:
            if query.message.photo or query.message.document:
                await query.edit_message_caption(caption=new_caption, parse_mode=ParseMode.HTML, reply_markup=None)
            else:
                await query.edit_message_text(text=new_caption, parse_mode=ParseMode.HTML, reply_markup=None)
        except Exception as e:
            logger.warning(f"Kanal xabarini tahrirlashda xatolik: {e}")

        # 2. Ota-onaga bildirishnoma yuborish
        try:
            await context.bot.send_message(
                chat_id=parent_id,
                text=(
                    "⚠️ <b>Hurmatli ota-ona!</b>\n\n"
                    "Siz yuborgan to'lov chekida kamchilik aniqlandi yoki to'lov tasdiqlanmadi.\n\n"
                    "Iltimos, chek ma'lumotlari (summa, sana, to'lovchi) to'g'riligini tekshirib, "
                    "qaytadan /menu orqali to'lov qiling yoki ma'muriyat bilan bog'laning:\n"
                    "📩 @Ipeschool44\n"
                    "📞 +998 55 588 50 00\n"
                    "📞 +998 71 295 11 05"
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.warning(f"Ota-onaga bildirishnoma yuborilmadi (user_id={parent_id}): {e}")

        await query.answer("❌ To'lov rad etildi va ota-onaga xabar yuborildi.")


async def handle_channel_free_lesson_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Bepul dars kanalidagi tugmalarni qayta ishlash:
    Callback data: adm_fl:<status>:<user_id>
    Statuslar: called, process, attended, active, inactive
    """
    query = update.callback_query
    admin_user = query.from_user
    chat = query.message.chat

    # Faqat adminlar
    if not await is_admin(context, admin_user.id, chat.id):
        await query.answer("⛔️ Bu tugmani faqat kanal administratorlari boshqara oladi!", show_alert=True)
        return

    parts = query.data.split(":")
    status_code = parts[1]
    parent_id = int(parts[2])
    admin_name = admin_user.full_name
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    status_labels = {
        "called": "📞 Gaplashildi",
        "process": "⏳ Jarayonda",
        "attended": "🎓 Sinov darsiga qatnashdi",
        "active": "🟢 Aktiv bo'ldi",
        "inactive": "🔴 Aktiv bo'lmadi",
    }
    label = status_labels.get(status_code, status_code)

    current_text = query.message.text or query.message.caption or ""

    # Agar avval status qo'shilgan bo'lsa, eskisini yangilaymiz yoki yangi status qo'shamiz
    base_text = current_text.split("\n\n━━━━━━━━━━━━━━━━━━━━\n📌 <b>Holat:</b>")[0]
    updated_text = (
        f"{base_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Holat:</b> {label}\n"
        f"👨‍💼 Mas'ul: {admin_name} ({now_str})"
    )

    # Agar "Aktiv bo'ldi" yoki "Aktiv bo'lmadi" yakuniy bosqich bo'lsa ham, tugmalarni yangilab saqlash yoki o'zgartirish imkonini qoldiramiz
    from keyboards import get_channel_free_lesson_keyboard

    # Yangi status tugmalarda ham aks etishi uchun qayta inline klaviatura qo'yamiz (yoki tugatilgan bo'lsa olib tashlash mumkin)
    # Faoliyatni davomiy boshqarish uchun klaviaturani qoldiramiz
    reply_markup = get_channel_free_lesson_keyboard(parent_id)

    try:
        await query.edit_message_text(
            text=updated_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.warning(f"Kanal xabarini yangilashda xatolik: {e}")

    # Agar status "active" bo'lsa — ota-onaga bildirishnoma yuboriladi!
    if status_code == "active":
        try:
            await context.bot.send_message(
                chat_id=parent_id,
                text=(
                    "🎉 <b>Tabriklaymiz!</b>\n\n"
                    "Farzandingiz <b>IPE School</b> o'quv markazimizning rasmiy o'quvchilar safiga qabul qilindi va "
                    "holati <b>Aktiv</b> etib belgilandi! 🌟\n\n"
                    "Dars jadvali va qo'shimcha ma'lumotlar bo'yicha kuratoringiz tez orada aloqaga chiqadi."
                ),
                parse_mode=ParseMode.HTML,
            )
            await query.answer("🟢 O'quvchi 'Aktiv' qilindi va ota-onaga bildirishnoma jo'natildi!", show_alert=True)
            return
        except Exception as e:
            logger.warning(f"Ota-onaga bildirishnoma jo'natishda xatolik: {e}")

    await query.answer(f"Status yangilandi: {label}")

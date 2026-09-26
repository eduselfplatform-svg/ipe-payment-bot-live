from datetime import datetime
from telegram import User


def format_payment_caption(user: User, user_data: dict) -> str:
    """
    To'lov cheki bilan birga PAYMENTS_CHANNEL ga yuboriladigan HTML formatdagi xabar (caption).
    """
    names_list = "\n".join(f"  {i + 1}. {name}" for i, name in enumerate(user_data.get("children_names", [])))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    username_str = f"@{user.username}" if user.username else "mavjud emas"

    caption = (
        "🆕 <b>Yangi to'lov — IPE School</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ota-ona:</b> {user.full_name} ({username_str})\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
        f"👶 <b>Farzandlar soni:</b> {user_data.get('child_count', 1)}\n"
        f"📋 <b>Ismlari:</b>\n{names_list}\n"
        f"🕒 <b>Sana:</b> {now_str}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ <i>Iltimos, ilova qilingan chekni tekshirib tasdiqlang.</i>"
    )
    return caption


def format_free_lesson_message(user: User, user_data: dict) -> str:
    """
    Bepul darsga yozilganlar bo'yicha FREE_LESSON_CHANNEL ga yuboriladigan HTML formatdagi xabar.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    username_str = f"@{user.username}" if user.username else "mavjud emas"

    text = (
        "🎁 <b>Bepul sinov darsiga yangi ariza — IPE School</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ota-ona:</b> {user_data.get('parent_name')}\n"
        f"👶 <b>Farzand:</b> {user_data.get('child_name')} ({user_data.get('child_age')})\n"
        f"📞 <b>Telefon:</b> {user_data.get('phone')}\n"
        f"📚 <b>Qiziqqan kurs:</b> {user_data.get('interested_course')}\n"
        f"🆔 <b>Telegram profil:</b> {user.full_name} ({username_str}, ID: <code>{user.id}</code>)\n"
        f"🕒 <b>Sana:</b> {now_str}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    return text

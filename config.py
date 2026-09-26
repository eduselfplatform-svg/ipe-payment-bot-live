import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _get_channel_id(env_var: str, default: str | None = None) -> int | str:
    val = os.getenv(env_var, default)
    if not val:
        return ""
    val = val.strip()
    # Raqam bo'lsa int ga o'tkazish (-100... kabi)
    if val.startswith("-") and val[1:].isdigit():
        return int(val)
    if val.isdigit():
        return int(val)
    return val


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID: int | str = _get_channel_id("CHANNEL_ID", "@ipe_school_channel")
PAYMENTS_CHANNEL_ID: int | str = _get_channel_id("PAYMENTS_CHANNEL_ID", "-1001234567890")
FREE_LESSON_CHANNEL_ID: int | str = _get_channel_id("FREE_LESSON_CHANNEL_ID", "-1009876543210")

MAX_CHILDREN: int = int(os.getenv("MAX_CHILDREN", "10"))
RUN_MODE: str = os.getenv("RUN_MODE", "polling").strip().lower()
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "").strip()
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "").strip()
PORT: int = int(os.getenv("PORT", "8080"))
CONVERSATION_TIMEOUT_SECONDS: int = int(os.getenv("CONVERSATION_TIMEOUT_SECONDS", "1800"))

# Adminlar ID ro'yxati (ixtiyoriy, agar bo'sh bo'lsa kanalda admin huquqiga ega bo'lganlar get_chat_member orqali tekshiriladi)
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]


def validate_config():
    """Bot ishga tushishidan oldin majburiy parametrlarni tekshiradi."""
    missing = []
    if not BOT_TOKEN or "your-bot-token" in BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not CHANNEL_ID:
        missing.append("CHANNEL_ID")
    if not PAYMENTS_CHANNEL_ID:
        missing.append("PAYMENTS_CHANNEL_ID")
    if not FREE_LESSON_CHANNEL_ID:
        missing.append("FREE_LESSON_CHANNEL_ID")

    if missing:
        print(f"⚠️ DIQQAT: Quyidagi muhit o'zgaruvchilari sozlanmagan: {', '.join(missing)}")
        print("Iltimos, .env faylini to'ldiring (.env.example ga qarang).")

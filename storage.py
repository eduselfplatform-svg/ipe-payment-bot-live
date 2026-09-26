import json
import os
import logging

logger = logging.getLogger(__name__)

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


def _load() -> list[int]:
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"users.json faylini o'qishda xatolik: {e}")
        return []


def _save(users: list[int]):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"users.json fayliga yozishda xatolik: {e}")


def save_user(chat_id: int):
    """Foydalanuvchi chat_id sini bazaga saqlaydi."""
    users = _load()
    if chat_id not in users:
        users.append(chat_id)
        _save(users)


def get_all_user_ids() -> list[int]:
    """Barcha ro'yxatdan o'tgan foydalanuvchilar chat_id larini qaytaradi."""
    return _load()


def remove_user(chat_id: int):
    """Botni bloklagan foydalanuvchini ro'yxatdan o'chirish."""
    users = _load()
    if chat_id in users:
        users.remove(chat_id)
        _save(users)

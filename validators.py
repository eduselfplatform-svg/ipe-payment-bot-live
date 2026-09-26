import re


def validate_not_empty(text: str | None, min_len: int = 3, max_len: int = 100) -> tuple[bool, str]:
    """
    Kiritilgan matn bo'sh emasligi va belgilangan uzunlikda ekanligini tekshiradi.
    """
    if not text:
        return False, "❗️ Iltimos, ma'lumotni matn ko'rinishida kiriting."
    
    cleaned = text.strip()
    if len(cleaned) < min_len:
        return False, f"❗️ Matn juda qisqa. Kamida {min_len} ta belgidan iborat bo'lishi kerak."
    
    if len(cleaned) > max_len:
        return False, f"❗️ Matn juda uzun. Ko'pi bilan {max_len} ta belgidan oshmasligi kerak."
    
    return True, cleaned


def validate_phone(text: str | None) -> tuple[bool, str]:
    """
    Telefon raqamini tekshiradi va standart +998XXXXXXXXX formatga keltiradi.
    """
    if not text:
        return False, "❗️ Iltimos, telefon raqamingizni kiriting."
    
    # Barcha bo'shliqlar, chiziqchalar va qavslarni olib tashlaymiz
    cleaned = re.sub(r"[\s\-\(\)]", "", text.strip())
    
    # +998901234567 yoki 998901234567 yoki 901234567 holatlarini moslash
    match = re.match(r"^(\+?998)?([0-9]{9})$", cleaned)
    if not match:
        return False, (
            "❗️ Telefon raqami noto'g'ri kiritildi.\n"
            "Misol: +998901234567 yoki 901234567"
        )
    
    formatted = f"+998{match.group(2)}"
    return True, formatted


def validate_int(text: str | None, min_v: int = 1, max_v: int = 10) -> tuple[bool, int | str]:
    """
    Raqam ekanligini va [min_v, max_v] oraliqda ekanini tekshiradi.
    """
    if not text:
        return False, f"❗️ Faqat {min_v}–{max_v} oralig'ida son kiriting."
    
    cleaned = text.strip()
    if not cleaned.isdigit():
        return False, f"❗️ Faqat {min_v}–{max_v} oralig'ida butun son kiriting."
    
    val = int(cleaned)
    if val < min_v or val > max_v:
        return False, f"❗️ Iltimos, {min_v} dan {max_v} gacha bo'lgan son kiriting."
    
    return True, val

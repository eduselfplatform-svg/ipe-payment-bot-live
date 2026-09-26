import logging
import sys
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

import config
from handlers.start import (
    start_command,
    menu_command,
    check_subscription_callback,
    back_to_menu_callback,
)
from handlers.courses import show_courses_menu, show_course_detail
from handlers.about import show_about_info
from handlers.payment import payment_conversation
from handlers.free_lesson import free_lesson_conversation
from handlers.admin import broadcast_conversation
from handlers.fallback import global_error_handler
from handlers.channel_actions import (
    handle_channel_payment_action,
    handle_channel_free_lesson_action,
)

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    """Telegram bot ilovasini qurish va handlerlarni ro'yxatdan o'tkazish."""
    config.validate_config()

    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! Botni ishga tushirish uchun .env faylini sozlang.")
        sys.exit(1)

    application = Application.builder().token(config.BOT_TOKEN).build()

    # 1. Flow ConversationHandler lar (birinchi ro'yxatga olinadi)
    application.add_handler(broadcast_conversation)
    application.add_handler(payment_conversation)
    application.add_handler(free_lesson_conversation)

    # 2. Buyruqlar (Commands)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))

    # 3. Pastki Reply klaviatura tugmalari uchun MessageHandler lar
    application.add_handler(MessageHandler(filters.Regex("^📚 Mavjud kurslar$"), show_courses_menu))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ Biz haqimizda$"), show_about_info))

    # 4. Kanal admin tugmalari handlerlari (adm_pay va adm_fl)
    application.add_handler(CallbackQueryHandler(handle_channel_payment_action, pattern=r"^adm_pay:"))
    application.add_handler(CallbackQueryHandler(handle_channel_free_lesson_action, pattern=r"^adm_fl:"))

    # 5. CallbackQuery handlerlar (kurslar, haqida, obuna tekshirish, orqaga)
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(show_courses_menu, pattern="^menu_courses$"))
    application.add_handler(CallbackQueryHandler(show_course_detail, pattern=r"^course:"))
    application.add_handler(CallbackQueryHandler(show_about_info, pattern="^menu_about$"))

    # 6. Global Error Handler
    application.add_error_handler(global_error_handler)

    return application


def main():
    """Botni tanlangan rejimda (polling yoki webhook) ishga tushirish."""
    application = build_application()

    if config.RUN_MODE == "webhook":
        logger.info(f"Bot Webhook rejimida ishga tushmoqda (PORT: {config.PORT})...")
        webhook_path = config.WEBHOOK_SECRET or "webhook"
        full_url = f"{config.WEBHOOK_URL.rstrip('/')}/{webhook_path}"

        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path=webhook_path,
            webhook_url=full_url,
            secret_token=config.WEBHOOK_SECRET if config.WEBHOOK_SECRET else None,
        )
    else:
        logger.info("Bot Polling rejimida ishga tushmoqda...")
        application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

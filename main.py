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


import asyncio
from aiohttp import web


async def health_check_handler(request):
    """Render Web Service port tekshiruvi (Health Check) uchun."""
    return web.Response(text="IPE School Payment Bot is running OK!")


async def run_dummy_server(port: int):
    """Render Web Service talab qiladigan PORT da oddiy HTTP server yuritadi."""
    app = web.Application()
    app.router.add_get("/", health_check_handler)
    app.router.add_get("/health", health_check_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check HTTP server {port}-portda ishga tushdi.")


async def run_bot_and_server():
    """Bot polling va HTTP health check serverini bitta jarayonda birgalikda ishlatish."""
    application = build_application()

    # Agar Render Web Service PORT bergan bo'lsa, uni tinglaymiz
    port = int(os.environ.get("PORT", config.PORT))
    try:
        await run_dummy_server(port)
    except Exception as e:
        logger.warning(f"HTTP serverni ishga tushirishda ogohlantirish (ehtimol port band): {e}")

    logger.info("Bot Polling rejimida ishga tushmoqda...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    # Doimiy ishlashni ushlab turish
    stop_event = asyncio.Event()
    await stop_event.wait()


def main():
    """Botni tanlangan rejimda (polling yoki webhook) ishga tushirish."""
    if config.RUN_MODE == "webhook":
        application = build_application()
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
        # Bitta serverda (Web Service - Free tier) polling va PORT listening
        import os
        if "PORT" in os.environ:
            asyncio.run(run_bot_and_server())
        else:
            application = build_application()
            logger.info("Bot Polling rejimida ishga tushmoqda...")
            application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

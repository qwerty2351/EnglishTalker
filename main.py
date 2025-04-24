import logging
from telegram.ext import ApplicationBuilder
from config import TOKEN
from handlers import register_handlers
from database.db_manager import init_db

# Настройка логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/bot.log", encoding="utf-8"),  # Указываем кодировку UTF-8
            logging.StreamHandler()
        ]
    )

# Обработчик ошибок
async def error_handler(update, context):
    logger = logging.getLogger(__name__)
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

def main():
    # Инициализация логирования
    setup_logging()
    
    # Инициализация базы данных
    init_db()

    # Создаем приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    register_handlers(app)

    # Регистрируем обработчик ошибок
    app.add_error_handler(error_handler)

    # Запускаем бота
    logging.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
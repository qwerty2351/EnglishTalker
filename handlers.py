import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from database.db_manager import (
    add_phrase_to_db, get_random_phrase, get_all_phrases, clear_database
)
from utils.translate_api import translate_text
from keyboard import get_main_keyboard, get_new_word_keyboard

# Логгер
logger = logging.getLogger(__name__)

# Состояния для диалогов
WAITING_FOR_TRANSLATION = 1
WAITING_FOR_ENGLISH = 2
WAITING_FOR_RUSSIAN = 3

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /start")
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе изучать английский язык. Выбери действие:\n\n"
        "📚 Добавить слово — расширь свой словарный запас.\n"
        "📖 Изучать слова — потренируй перевод.\n"
        "📋 Показать все слова — просмотреть добавленные фразы.\n"
        "🌐 Перевести текст — переведи любой текст на английский.",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

# Команда /reset
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /reset")
    await start(update, context)

# Команда /translate
async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /translate")
    await update.message.reply_text("Пожалуйста, отправьте текст для перевода на английский язык.")
    return WAITING_FOR_TRANSLATION

async def handle_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Пользователь {update.effective_user.id} отправил текст для перевода: {user_message}")
    
    if not user_message.strip():
        await update.message.reply_text("Пожалуйста, введите текст для перевода.")
        return WAITING_FOR_TRANSLATION
    
    try:
        translated_text = await translate_text(user_message, target_language="en")
        await update.message.reply_text(f"Перевод: {translated_text}")
    except Exception as e:
        logger.error(f"Ошибка при переводе: {e}")
        await update.message.reply_text("Не удалось выполнить перевод. Попробуйте позже.")
    
    return ConversationHandler.END

# Команда /add
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /add")
    await update.message.reply_text("Пожалуйста, отправьте слово или предложение на английском языке.")
    return WAITING_FOR_ENGLISH

async def get_english_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    english_text = update.message.text
    logger.info(f"Пользователь {update.effective_user.id} отправил английский текст: {english_text}")
    
    if not english_text.strip():
        await update.message.reply_text("Пожалуйста, введите корректный текст на английском языке.")
        return WAITING_FOR_ENGLISH
    
    context.user_data["english_text"] = english_text
    await update.message.reply_text("Теперь отправьте перевод этого текста на русский язык.")
    return WAITING_FOR_RUSSIAN

async def get_russian_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    russian_text = update.message.text
    logger.info(f"Пользователь {update.effective_user.id} отправил русский текст: {russian_text}")
    
    if not russian_text.strip():
        await update.message.reply_text("Пожалуйста, введите корректный перевод на русском языке.")
        return WAITING_FOR_RUSSIAN
    
    english_text = context.user_data.get("english_text")
    add_phrase_to_db(english_text, russian_text)
    await update.message.reply_text(
        f"Фраза '{english_text}' с переводом '{russian_text}' добавлена!",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

# Команда /phrases
async def show_all_phrases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        message_object = query.message
    else:
        message_object = update.message

    phrases = get_all_phrases()
    if phrases:
        message = "Все доступные фразы:\n" + "\n".join([f"{phrase} - {translation}" for phrase, translation in phrases])
    else:
        message = "Словарь пуст. Добавьте фразы с помощью команды /add."
    
    await message_object.reply_text(message, reply_markup=get_main_keyboard())

# Команда /clear
async def clear_database_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /clear")
    clear_database()
    await update.message.reply_text("База данных успешно очищена!", reply_markup=get_main_keyboard())

# Изучение слов (англ → рус)
async def learn_en_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        message_object = query.message
    else:
        message_object = update.message

    phrase, translation = get_random_phrase()
    if not phrase or not translation:
        await message_object.reply_text("Словарь пуст. Добавьте слова с помощью команды /add.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    context.user_data["current_phrase"] = phrase
    context.user_data["current_translation"] = translation
    context.user_data["current_command"] = "learn_en_ru"
    await message_object.reply_text(f"Переведите слово/предложение: {phrase}")

# Изучение слов (рус → англ)
async def learn_ru_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        message_object = query.message
    else:
        message_object = update.message

    phrase, translation = get_random_phrase()
    if not phrase or not translation:
        await message_object.reply_text("Словарь пуст. Добавьте слова с помощью команды /add.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    context.user_data["current_phrase"] = translation
    context.user_data["current_translation"] = phrase
    context.user_data["current_command"] = "learn_ru_en"
    await message_object.reply_text(f"Переведите слово/предложение: {translation}")

# Проверка ответа пользователя
async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.lower()
    correct_translation = context.user_data.get("current_translation", "").lower()
    
    logger.info(f"Пользователь {update.effective_user.id} отправил ответ: {user_answer}")
    
    if user_answer == correct_translation:
        response = "Правильно! 🎉"
    else:
        response = f"Неправильно. Правильный ответ: {correct_translation}"
    
    command = context.user_data.get("current_command")
    if command == "learn_en_ru":
        await learn_en_ru(update, context)
    elif command == "learn_ru_en":
        await learn_ru_en(update, context)
    
    await update.message.reply_text(response, reply_markup=get_main_keyboard())
    return ConversationHandler.END

# Обработка нажатия на кнопки
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем обработку запроса

    if query.data == "add_word":
        await add_command(update, context)
    elif query.data == "learn_en_ru":
        await learn_en_ru(update, context)
    elif query.data == "learn_ru_en":
        await learn_ru_en(update, context)
    elif query.data == "show_phrases":
        await show_all_phrases(update, context)
    elif query.data == "translate_text":
        await translate_command(update, context)

# Регистрация обработчиков
def register_handlers(app):
    conv_handler_translate = ConversationHandler(
        entry_points=[CommandHandler("translate", translate_command)],
        states={
            WAITING_FOR_TRANSLATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_translation)],
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler_translate)

    conv_handler_add = ConversationHandler(
        entry_points=[CommandHandler("add", add_command)],
        states={
            WAITING_FOR_ENGLISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_english_text)],
            WAITING_FOR_RUSSIAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_russian_text)],
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler_add)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("learn_en_ru", learn_en_ru))
    app.add_handler(CommandHandler("learn_ru_en", learn_ru_en))
    app.add_handler(CommandHandler("phrases", show_all_phrases))
    app.add_handler(CommandHandler("clear", clear_database_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))
    app.add_handler(CallbackQueryHandler(handle_callback_query))  # Обработчик инлайн-кнопок
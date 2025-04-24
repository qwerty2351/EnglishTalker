from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """
    Создает инлайн-клавиатуру для приветственного сообщения.
    """
    keyboard = [
        [InlineKeyboardButton("Добавить слово", callback_data="add_word")],
        [InlineKeyboardButton("Изучать слова (англ → рус)", callback_data="learn_en_ru")],
        [InlineKeyboardButton("Изучать слова (рус → англ)", callback_data="learn_ru_en")],
        [InlineKeyboardButton("Показать все слова", callback_data="show_phrases")],
        [InlineKeyboardButton("Перевести текст", callback_data="translate_text")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_new_word_keyboard():
    """
    Создает инлайн-клавиатуру с кнопкой "Получить новое слово".
    """
    keyboard = [
        [InlineKeyboardButton("Получить новое слово", callback_data="new_word")]
    ]
    return InlineKeyboardMarkup(keyboard)
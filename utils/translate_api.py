from googletrans import Translator

async def translate_text(text, target_language="en"):
    """
    Переводит текст на указанный язык.
    """
    translator = Translator()
    translation = await translator.translate(text, dest=target_language)
    return translation.text
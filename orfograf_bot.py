import logging
import requests
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ----- ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ -----
# Данный токен публично доступен, что небезопасно!
# Рекомендуется хранить такие секреты в переменных окружения или
# в файлах, не попадающих под версионный контроль.

TELEGRAM_BOT_TOKEN = "7269384673:AAF7HlYzmX8OK5_h1hUjFtODtxghWSB3j7M"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start."""
    await update.message.reply_text(
        "Привет! Я бот для проверки орфографии.\n"
        "Отправьте мне текст — попробую его исправить!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /help."""
    await update.message.reply_text(
        "Отправьте мне любой русский текст, а я постараюсь найти и "
        "исправить орфографические ошибки."
    )

# Пример проверки орфографии (через Yandex.Speller) — как демонстрация
def check_spelling_yandex_speller(text: str) -> str:
    url = "https://speller.yandex.net/services/spellservice.json/checkText"
    params = {
        "text": text,
        "lang": "ru"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        corrected_text = text
        shift = 0
        for err in data:
            if err["s"]:
                replacement = err["s"][0]
                start_pos = err["pos"] + shift
                end_pos = start_pos + err["len"]
                corrected_text = (
                    corrected_text[:start_pos]
                    + replacement
                    + corrected_text[end_pos:]
                )
                shift += len(replacement) - err["len"]

        return corrected_text
    except requests.RequestException as e:
        logging.error(f"Ошибка при обращении к Yandex.Speller: {e}")
        return text

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычного текстового сообщения от пользователя."""
    user_text = update.message.text

    # Проверяем орфографию (пример с Yandex.Speller)
    corrected_text = check_spelling_yandex_speller(user_text)

    # Можно дополнительно вызвать любую другую модель/библиотеку, если нужно.
    # ...

    await update.message.reply_text(
        f"Исходный текст:\n{user_text}\n\n"
        f"Исправленный текст:\n{corrected_text}"
    )

async def main():
    """Запуск бота."""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

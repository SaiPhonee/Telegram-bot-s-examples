import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from pyaspeller import YandexSpeller

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация YandexSpeller
speller = YandexSpeller()

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь мне текст, и я проверю его на орфографию и грамматику.")

# Функция для применения исправлений к тексту
def apply_corrections(text, corrections):
    # Сортируем исправления по позиции в тексте (от конца к началу)
    corrections = sorted(corrections, key=lambda x: x['pos'], reverse=True)
    for correction in corrections:
        start_pos = correction['pos']
        end_pos = start_pos + len(correction['word'])
        # Заменяем слово с ошибкой на исправленное
        text = text[:start_pos] + correction['s'][0] + text[end_pos:]
    return text

# Обработчик текстовых сообщений
async def check_text(update: Update, context):
    text = update.message.text
    corrections = speller.spell(text)

    if not corrections:
        await update.message.reply_text("Ошибок не найдено!")
    else:
        corrected_text = apply_corrections(text, corrections)
        await update.message.reply_text(f"Найдены ошибки:\n\nИсправленный текст:\n{corrected_text}")

# Основная функция для запуска бота
def main():
    # Вставьте сюда ваш токен
    application = Application.builder().token("8131839408:AAF3K8ip2aaDBqxLrDgF9NAifbJvFIUdaxo").build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_text))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
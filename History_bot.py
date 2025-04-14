import logging
import sqlite3
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import language_tool_python

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
conn = sqlite3.connect("bot_users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT
)
""")
conn.commit()

# Инициализация LanguageTool для русского языка
tool = language_tool_python.LanguageTool('ru')


# Функция для регистрации пользователей в базе данных
def register_user(update: Update):
    user = update.message.from_user
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                   (user.id, user.username, user.first_name, user.last_name))
    conn.commit()
    logger.info(f"Новый пользователь: {user.id} - {user.username} ({user.first_name} {user.last_name})")


# Функция для обработки команд /start
async def start(update: Update, context: CallbackContext):
    register_user(update)
    # Определяем кнопки
    keyboard = [["Помощь"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    # Приветственное сообщение
    await update.message.reply_text(
        "Привет! Я бот для проверки орфографии. Выбери действие или напиши текст, чтобы я его проверил.",
        reply_markup=reply_markup
    )


# Функция для проверки орфографии
async def check_word(update: Update, context: CallbackContext):
    register_user(update)
    text = update.message.text.strip()

    if text == "Помощь":
        await help_command(update, context)
        return

    # Приведение текста к стандартной форме для игнорирования регистра
    normalized_text = text[0].upper() + text[1:] if text else text
    matches = tool.check(normalized_text)

    if not matches:
        await update.message.reply_text(f"✅ \"{text}\" написано правильно!")
    else:
        errors = []
        for match in matches:
            suggestion = ", ".join(match.replacements) if match.replacements else "нет предложений"
            errors.append(f"Ошибка: {match.message}\nИсправление: {suggestion}")

        error_text = "\n\n".join(errors)
        await update.message.reply_text(
            f"❌ Обнаружены ошибки в тексте:\n\n{error_text}"
        )
    logger.info(f"Пользователь {update.message.from_user.id} проверил текст: {text}")


# Функция для обработки кнопки "Помощь"
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Вот что я могу делать:\n"
        "- Проверить текст на орфографические ошибки: просто отправьте текст.\n"
        "- Использовать кнопки для быстрого взаимодействия.\n\n"
        "Если у вас есть вопросы, выберите 'Помощь'!"
    )


# Функция для получения списка пользователей (админ-функция)
async def get_users(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.username != "saiphoneee" and user.username != 'JustLechka' and user.username != 'qratis':  # Замените на свой Telegram username
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    cursor.execute("SELECT user_id, username, first_name, last_name FROM users")
    users = cursor.fetchall()
    user_list = "\n".join([f"ID: {u[0]}, Username: {u[1]}, Имя: {u[2]}, Фамилия: {u[3]}" for u in users])
    await update.message.reply_text(f"Зарегистрированные пользователи:\n\n{user_list}")


# Основная функция для запуска бота
def main():
    # Вставьте сюда токен вашего бота
    TOKEN = "8131839408:AAF3K8ip2aaDBqxLrDgF9NAifbJvFIUdaxo"

    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get_users", get_users))  # Админ-команда
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_word))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()

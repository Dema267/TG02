import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# URL-ссылки
URLS = {
    "news": "https://radiotapok.ru/",
    "music": "https://musify.club/track/radio-tapok-zloi-gorod-20667354",
    "video": "https://www.bing.com/videos/riverview/relatedvideo?q=%D1%80%D0%B0%D0%B4%D0%B8%D0%BE+%D1%82%D0%B0%D0%BF%D0%BE%D0%BA&mid=C53FD9D2661703693627C53FD9D2661703693627&FORM=VIRE"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text(
        "Привет! Я бот с полезными ссылками. Используй команду /links чтобы получить доступ к ресурсам."
    )

async def send_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с инлайн-кнопками ссылок."""
    keyboard = [
        [
            InlineKeyboardButton("Новости", url=URLS["news"]),
            InlineKeyboardButton("Музыка", url=URLS["music"]),
        ],
        [InlineKeyboardButton("Видео", url=URLS["video"])],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите интересующий вас ресурс:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает клики по инлайн-кнопкам."""
    query = update.callback_query
    await query.answer()

def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("links", send_links))

    # Регистрация обработчика инлайн-кнопок
    application.add_handler(CallbackQueryHandler(button_click))

    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
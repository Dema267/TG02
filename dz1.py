import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Состояния для ConversationHandler
GET_NAME, SHOW_MENU = range(2)

# Текст кнопок
BUTTON_HELLO = "Привет"
BUTTON_BYE = "Пока"

# Клавиатура меню
menu_keyboard = ReplyKeyboardMarkup(
    [[BUTTON_HELLO, BUTTON_BYE]],
    resize_keyboard=True,
    one_time_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start, запрашивает имя пользователя."""
    await update.message.reply_text(
        "Привет! Я бот с меню. Как тебя зовут?"
    )
    return GET_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает имя пользователя и показывает меню."""
    user_name = update.message.text
    context.user_data["user_name"] = user_name

    await update.message.reply_text(
        f"Отлично, {user_name}! Выбери действие:",
        reply_markup=menu_keyboard
    )
    return SHOW_MENU


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает нажатия кнопок в меню."""
    user_name = context.user_data.get("user_name", "друг")
    text = update.message.text

    if text == BUTTON_HELLO:
        await update.message.reply_text(f"Привет, {user_name}!")
    elif text == BUTTON_BYE:
        await update.message.reply_text(f"До свидания, {user_name}!")

    # Показываем меню снова
    await update.message.reply_text(
        "Выбери следующее действие:",
        reply_markup=menu_keyboard
    )
    return SHOW_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет диалог."""
    await update.message.reply_text(
        "Диалог завершен. Нажми /start чтобы начать заново.",
        reply_markup=None
    )
    return ConversationHandler.END


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()

    # ConversationHandler для управления диалогом
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SHOW_MENU: [MessageHandler(filters.Regex(f"^({BUTTON_HELLO}|{BUTTON_BYE})$"), show_menu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
import logging
import os
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import requests

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
KINOPOISK_API_KEY = os.getenv("KINOPOISK_API_KEY")

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Клавиатура главного меню (без кнопки "Поиск по жанру")
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🔍 Поиск сериала")],
            [KeyboardButton("🏆 Топ-10 сериалов")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

# Получение информации о сериале
async def get_series_info(series_id: int):
    url = f"https://api.kinopoisk.dev/v1.4/movie/{series_id}"
    headers = {"X-API-KEY": KINOPOISK_API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка API: {e}")
        return None

# Поиск сериалов по названию
async def search_series(query: str):
    url = "https://api.kinopoisk.dev/v1.4/movie/search"
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    params = {
        "page": 1,
        "limit": 5,
        "query": query,
        "type": "tv-series"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("docs", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка API: {e}")
        return []

# Получение топ-10 сериалов
async def get_top_series():
    url = "https://api.kinopoisk.dev/v1.4/movie"
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    params = {
        "page": 1,
        "limit": 10,
        "type": "tv-series",
        "sortField": "votes.kp",
        "sortType": "-1"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("docs", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка API: {e}")
        return []

# Форматирование информации о сериале
async def format_series_info(series):
    name = series.get('name', 'Название неизвестно')
    rating = series.get('rating', {}).get('kp', 0)
    genres = ", ".join([g['name'] for g in series.get('genres', [])[:3]])
    poster_url = series.get('poster', {}).get('url', '')
    web_url = f"https://www.kinopoisk.ru/film/{series.get('id', '')}/"
    year = series.get('year', '')

    # Актеры (первые 3)
    actors = []
    for person in series.get('persons', []):
        if person.get('enProfession') == 'actor':
            actors.append(person.get('name', ''))
            if len(actors) >= 3:
                break
    actors_str = ", ".join(actors) if actors else "не указано"

    info_text = (
        f"<b>🎬 {name}</b>\n"
        f"⭐ Рейтинг: <b>{rating:.1f}</b>\n"
        f"📌 Жанры: <b>{genres}</b>\n"
        f"📅 Год: <b>{year}</b>\n"
        f"🎭 Актеры: <b>{actors_str}</b>\n\n"
    )

    if poster_url:
        info_text += f"<a href='{poster_url}'>🔗 Постер</a>\n"
    if web_url:
        info_text += f"<a href='{web_url}'>🌐 Подробнее на Кинопоиске</a>"

    return info_text

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"🍿 Привет, {user.first_name}!\n"
        "Я помогу тебе найти интересные сериалы.\n"
        "Используй кнопки ниже для навигации:",
        reply_markup=get_main_keyboard()
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "ℹ️ *Помощь по боту*\n\n"
        "Этот бот помогает находить информацию о сериалах:\n"
        "- 🔍 Поиск сериалов по названию\n"
        "- 🏆 Просмотр топ-10 сериалов\n\n"
        "После поиска вы увидите:\n"
        "- Название и жанр\n"
        "- Рейтинг\n"
        "- Актерский состав\n"
        "- Год выпуска\n"
        "- Ссылку на Кинопоиск для подробной информации\n\n"
        "Для начала работы нажмите /start или используйте кнопки меню."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "🔍 Поиск сериала":
        await update.message.reply_text("Введите название сериала:")
        context.user_data['awaiting_search'] = True

    elif text == "🏆 Топ-10 сериалов":
        await show_top_series(update, context)

    elif 'awaiting_search' in context.user_data:
        await process_search(update, context)

# Показать топ сериалов
async def show_top_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Загружаю топ-10 сериалов...")

    top_series = await get_top_series()

    if not top_series:
        await update.message.reply_text("😕 Не удалось загрузить топ сериалов. Попробуйте позже.")
        return

    for series in top_series[:10]:
        series_info = await format_series_info(series)
        await update.message.reply_text(
            series_info,
            parse_mode="HTML"
        )

    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

# Обработка поиска по названию
async def process_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"🔍 Ищу сериалы по запросу: {query}...")

    results = await search_series(query)

    if not results:
        await update.message.reply_text("😕 Ничего не найдено. Попробуйте другой запрос.")
        del context.user_data['awaiting_search']
        return

    for series in results[:3]:  # Показываем первые 3 результата
        series_info = await format_series_info(series)
        await update.message.reply_text(
            series_info,
            parse_mode="HTML"
        )

    del context.user_data['awaiting_search']
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()

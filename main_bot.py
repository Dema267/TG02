import os
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise ValueError("Не задан TELEGRAM_BOT_TOKEN в .env")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем папки
IMG_DIR = Path("img")
IMG_DIR.mkdir(exist_ok=True)
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

# Проверяем наличие голосового сообщения
VOICE_PATH = ASSETS_DIR / "voice.ogg"
if not VOICE_PATH.exists():
    logger.warning(f"Голосовое сообщение не найдено по пути {VOICE_PATH}")


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я многофункциональный бот. Вот что я умею:\n"
        "- Сохранять все фото (/save_photo)\n"
        "- Отправлять голосовые сообщения (/voice)\n"
        "- Переводить текст на английский (/translate)\n\n"
        "Используй /help для списка команд"
    )


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Справка\n"
        "/info - Информация о боте\n"
        "/voice - Получить голосовое сообщение\n"
        "/translate - Перевести текст\n\n"
        "Просто отправьте:\n"
        "- Фото (я его сохраню)\n"
        "- Текст (я переведу его)"
    )
    await message.answer(help_text)


# Обработчик команды /info
@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    info_text = (
        "Многофункциональный бот v1.1\n"
        "Функции:\n"
        "1. Сохранение фото\n"
        "2. Отправка голосовых сообщений\n"
        "3. Перевод текста\n"
        "Разработчик: Зарецкий Максим"
    )
    await message.answer(info_text)


# Обработчик команды /voice
@dp.message(Command("voice"))
async def cmd_voice(message: types.Message):
    if VOICE_PATH.exists():
        voice = FSInputFile(VOICE_PATH)
        await message.answer_voice(voice)
    else:
        await message.answer("Извините, голосовое сообщение временно недоступно")


# Обработчик команды /translate
@dp.message(Command("translate"))
async def cmd_translate(message: types.Message):
    await message.answer("Отправьте текст для перевода на английский:")


# Обработчик фото
@dp.message(F.photo)
async def save_photo(message: types.Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    photo_bytes = await bot.download_file(file_path)

    save_path = IMG_DIR / f"{file_id}.jpg"
    with open(save_path, "wb") as f:
        f.write(photo_bytes.read())

    await message.answer(f"Фото сохранено как {save_path.name}")


# Обработчик текста (перевод)
@dp.message(F.text & ~F.text.startswith('/'))
async def handle_text(message: types.Message):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(message.text)
        await message.answer(f"Перевод на английский:\n{translated}")
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await message.answer("Ошибка перевода. Попробуйте позже.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
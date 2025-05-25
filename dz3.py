import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Кнопки
def get_initial_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Показать больше", callback_data="show_more")
    return builder.as_markup()

def get_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Опция 1", callback_data="option_1")
    builder.button(text="Опция 2", callback_data="option_2")
    builder.adjust(2)
    return builder.as_markup()

# ✅ Команда /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Используй /dynamic, чтобы увидеть динамическую клавиатуру.")

# ✅ Команда /dynamic
@router.message(Command("dynamic"))
async def cmd_dynamic(message: types.Message):
    await message.answer("🔘 Нажми кнопку ниже:", reply_markup=get_initial_keyboard())

# Обработка "Показать больше"
@router.callback_query(F.data == "show_more")
async def on_show_more(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=get_options_keyboard())
    await callback.answer()

# Обработка выбора опции
@router.callback_query(F.data.in_({"option_1", "option_2"}))
async def on_option_selected(callback: types.CallbackQuery):
    text = "✅ Вы выбрали: Опция 1" if callback.data == "option_1" else "✅ Вы выбрали: Опция 2"
    await callback.message.answer(text)
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

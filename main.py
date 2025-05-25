import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN
import keyboard as kb

from gtts import gTTS
import os

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command('voice'))
async def voice(message: Message):
    voice = FSInputFile("sample.ogg")
    await message.answer_voice(voice)

@dp.message(Command('audio'))
async def audio(message: Message):
    audio = FSInputFile('sound.mp3')
    await bot.send_audio(message.chat.id, audio)

@dp.message(Command('photos', prefix='&'))
async def photo(message: Message):
    photo_urls = [
        "https://avatars.mds.yandex.net/i?id=4d0e2edf9a1f8de64a03bf25ac93a071_l-5296622-images-thumbs&n=13",
        "https://avatars.mds.yandex.net/i?id=854005a8ce269f04258f3e88f3115308d8d5ad2b-9181356-images-thumbs&n=13"
    ]
    rand_photo = random.choice(photo_urls)
    await message.answer_photo(photo=rand_photo, caption='Это супер крутая картинка')

@dp.message(F.photo)
async def react_photo(message: Message):
    responses = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    await message.answer(random.choice(responses))
    await bot.download(message.photo[-1], destination=f'img/{message.photo[-1].file_id}.jpg')

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/photo")

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=kb.inline_keyboard_test)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

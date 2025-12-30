from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.types import BufferedInputFile
from aiogram.filters import CommandStart
from aiogram import F
import asyncio
from gtts import gTTS
from io import BytesIO
import random

with open("words.txt", "r", encoding="utf-8") as f:
    WORD_LIST = f.read().split()

# 1. Токен
import os
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Переменная BOT_TOKEN не задана!")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# 2. /start
@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Я бот Артёмки 🎵 Напиши что-нибудь — я повторю и озвучу!")

# 3. Озвучка текста → MP3 в памяти
async def text_to_speech(text: str) -> BytesIO:
    tts = gTTS(text=text, lang='ru', slow=False)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

#3.1 Генерация ответа из случайных слов
def generate_random_words(count: int = 25) -> str:
    """Возвращает строку из `count` случайных слов, разделённых пробелами"""
    words = random.choices(WORD_LIST, k=count)  # с повторениями (веселее!)
    # Или: random.sample(WORD_LIST, k=min(count, len(WORD_LIST))) — без повторений
    return " ".join(words)

# 4. Обработчик текста
@router.message(F.text)
async def echo_handler(message: Message):
    text = message.text
    await message.answer(f"Ты написал: {text}")

    # Озвучка
    try:
        audio_stream = await text_to_speech(text)
        audio_bytes = audio_stream.getvalue()
        audio_input = BufferedInputFile(file=audio_bytes, filename="artemka.mp3")
        await message.reply_audio(audio_input, title="Артёмка сказал", performer="Бот-папа")
    except Exception as e:
        await message.answer(f"Не смог озвучить 😢 Ошибка: {e}")

    # ➕ Генерация и отправка своих слов
    bot_words = generate_random_words(count=25)
    await message.answer(f"\n{bot_words}")


# 5. Запуск
async def main():
    dp.include_router(router)
    print("🎙️ Бот запущен! Говори — я запишу!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
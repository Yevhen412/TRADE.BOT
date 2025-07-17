import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from main import connect  # Импортируем WebSocket-цикл

import os

# Получаем токен и chat_id из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Логгирование (по желанию)
logging.basicConfig(level=logging.INFO)

running = False
last_run_time = 0

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    global running, last_run_time

    if str(message.chat.id) != CHAT_ID:
        await message.reply("⛔️ У вас нет доступа.")
        return

    now = asyncio.get_event_loop().time()
    if running:
        await message.answer("⚠️ Бот уже работает.")
        return

    if now - last_run_time < 180:  # 3 минуты
        await message.answer("⏳ Подождите минимум 3 минуты между запусками.")
        return

    running = True
    last_run_time = now
    await message.answer("▶️ Бот запущен на 2 минуты...")

    try:
        await asyncio.wait_for(connect(), timeout=120)
    except asyncio.TimeoutError:
        await message.answer("⏹️ Время вышло. Бот остановлен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        running = False

if __name__ == "__main__":
    print("🟡 Ожидание команды /start...")
    executor.start_polling(dp, skip_updates=True)

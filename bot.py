import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from websocket_client import run_session
from telegram_notifier import send_telegram_message

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Глобальный флаг — идёт ли сессия
is_session_running = False

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    global is_session_running

    if str(message.chat.id) != CHAT_ID:
        return

    if is_session_running:
        await message.reply("⏳ Уже идёт сессия...")
        return

    is_session_running = True
    await message.reply("✅ Сессия запущена. Работаем 2 минуты...")

    await run_session(duration_seconds=120, chat_id=CHAT_ID)

    await message.reply("⏹️ Сессия завершена.")
    is_session_running = False

if __name__ == "__main__":
    executor.start_polling(dp)

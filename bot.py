import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
import os

from websocket_client import connect_websocket

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

active_session = False

@dp.message_handler(commands=["start"])
async def handle_start(message: Message):
    global active_session

    if str(message.chat.id) != str(CHAT_ID):
        await message.answer("⛔️ Доступ запрещён.")
        return

    if active_session:
        await message.answer("⚠️ Сессия уже активна.")
        return

    active_session = True
    await message.answer("🚀 Запуск сессии...")
    try:
        await connect_websocket(duration_seconds=120)
    except Exception as e:
        await message.answer(f"[ERROR] {e}")
    finally:
        active_session = False
        await message.answer("🛑 Сессия завершена.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

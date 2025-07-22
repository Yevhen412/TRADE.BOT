import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os

from websocket_client import run_trading_session

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

session_active = False
cooldown = False

async def send_telegram_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

@dp.message(Command("start"))
async def handle_start(message: Message):
    global session_active, cooldown
    if session_active:
        await send_telegram_message("⚠️ Сессия уже активна!")
        return
    if cooldown:
        await send_telegram_message("⏳ Подождите перед следующим запуском.")
        return

    session_active = True
    await send_telegram_message("✅ Сессия запущена на 2 минуты...")

    await run_trading_session(send_telegram_message)

    await send_telegram_message("📉 Сессия завершена.")
    session_active = False
    cooldown = True
    await asyncio.sleep(180)  # 3 минуты ожидания
    cooldown = False

async def polling_loop():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(polling_loop())

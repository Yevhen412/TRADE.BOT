import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
from websocket_client import run_trading_session  # живая торговля

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

session_active = False

async def send_telegram_message(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

@dp.message(Command("start"))
async def handle_start(message: Message):
    global session_active
    if session_active:
        await send_telegram_message("⚠️ Сессия уже активна. Подожди завершения.")
        return

    session_active = True
    await send_telegram_message("✅ Сессия запущена на 2 минуты...")

    try:
        await run_trading_session(send_telegram_message, duration_seconds=120)
    except Exception as e:
        logging.error(f"Ошибка в торговой сессии: {e}")
        await send_telegram_message("❌ Произошла ошибка в сессии.")
    finally:
        session_active = False
        await send_telegram_message("⛔️ Сессия завершена. Торговля отключена.")

async def polling_loop():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(polling_loop())

import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold
from aiogram import Router
from aiogram.filters import Command

from telegram_notifier import send_telegram_message
from trade_simulator import run_trading_session

TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

session_running = False

@router.message(Command("start"))
async def handle_start(message: Message):
    global session_running

    if str(message.chat.id) != str(ALLOWED_CHAT_ID):
        await message.answer("❌ У вас нет доступа.")
        return

    if session_running:
        await message.answer("⚠️ Сессия уже запущена. Пожалуйста, дождитесь завершения.")
        return

    session_running = True
    await message.answer("✅ Сессия запущена на 2 минуты...")

    try:
        result_text = await run_trading_session()
        await message.answer(result_text)
    except Exception as e:
        await message.answer(f"❌ Ошибка в сессии: {e}")
    finally:
        session_running = False

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

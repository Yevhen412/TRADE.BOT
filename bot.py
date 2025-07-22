import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router

from websocket_client import connect_websocket
from telegram_notifier import send_telegram_message

import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

session_active = False  # Флаг, чтобы избежать автоповтора

@router.message(CommandStart())
async def start_command(message: Message):
    global session_active
    if session_active:
        await message.answer("⚠️ Сессия уже запущена. Подождите окончания.")
        return
    session_active = True
    await message.answer("✅ Сессия запущена на 2 минуты…")
    asyncio.create_task(run_session())

async def run_session():
    global session_active
    try:
        print("🔁 Стартую сессию WebSocket на 2 минуты")
        await send_telegram_message("🔁 Сессия WebSocket стартует")
        await connect_websocket(duration_seconds=120)
        await send_telegram_message("⏹️ Сессия завершена. Нажмите /start для нового запуска")
    except Exception as e:
        print("❌ Ошибка в run_session:", e)
        await send_telegram_message(f"❌ Ошибка: {e}")
    finally:
        session_active = False

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

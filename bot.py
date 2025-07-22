import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os
from websocket_client import run_trading_session

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Флаг состояния торговой сессии
session_active = False

@dp.message(Command("start"))
async def handle_start(message: types.Message):
    global session_active
    if session_active:
        await message.answer("⚠️ Сессия уже активна. Дождитесь завершения.")
        return

    session_active = True
    await message.answer("✅ Сессия запущена на 2 минуты...")
    
    # Запуск торговой сессии
    await run_trading_session()

    await message.answer("⛔️ Сессия завершена. Торговля отключена.")
    session_active = False

async def polling_loop():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(polling_loop())

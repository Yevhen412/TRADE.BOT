import asyncio
from aiogram import Bot, Dispatcher, types, executor
from websocket_client import connect_websocket
from telegram_notifier import send_telegram_message

import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("✅ Сессия запущена на 2 минуты…")
    asyncio.create_task(run_session())

async def run_session():
    try:
        print("🔁 Стартую сессию WebSocket на 2 минуты")
        await send_telegram_message("🔁 Сессия WebSocket стартует")
        await connect_websocket(duration_seconds=120)
        await send_telegram_message("⏹️ Сессия завершена. Нажмите /start для нового запуска")
    except Exception as e:
        print("❌ Ошибка в run_session:", e)
        await send_telegram_message(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

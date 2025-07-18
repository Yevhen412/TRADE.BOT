from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import time
from websocket_client import run_session
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

is_running = False
last_run_time = 0

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global is_running, last_run_time
    now = time.time()

    if is_running:
        await message.answer("Сессия уже запущена. Подожди.")
        return

    if now - last_run_time < 180:
        wait_time = int(180 - (now - last_run_time))
        await message.answer(f"Подожди {wait_time} секунд перед следующим запуском")
        return

    await message.answer("Сессия запущена на 2 минуты.")
    is_running = True
    last_run_time = now

    async def session_task():
        global is_running
        try:
            await run_session()
        except Exception as e:
            await message.answer(f"Ошибка: {e}")
        await asyncio.sleep(120)
        is_running = False
        await message.answer("Сессия завершена. Ожидаем 3 минуты.")

    asyncio.create_task(session_task())

if __name__ == "__main__":
    executor.start_polling(dp)

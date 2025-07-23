import asyncio
import signal
import sys
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router

from websocket_client import connect_websocket
from telegram_notifier import send_telegram_message

# === Переменные окружения ===
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# === Инициализация бота и диспетчера ===
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

session_running = False  # Флаг контроля сессии

# === Обработчик SIGTERM ===
def handle_sigterm(*_):
    print("🛑 SIGTERM получен ботом. Завершаем...")
    sys.exit(0)

# === Обработка команды /start ===
@router.message(CommandStart())
async def start_command(message: Message):
    global session_running
    if session_running:
        await message.answer("⚠️ Сессия уже запущена. Дождитесь завершения.")
        return

    session_running = True
    await message.answer("✅ Сессия запущена на 2 минуты…")
    asyncio.create_task(run_session())

# === Запуск сессии ===
async def run_session():
    global session_running
    try:
        await send_telegram_message("🚀 Начинаю 2-минутную сессию живой торговли")
        await connect_websocket(duration_seconds=120)
        await send_telegram_message("⏹️ Сессия завершена. Нажмите /start для новой.")
    except Exception as e:
        await send_telegram_message(f"❌ Ошибка в сессии: {e}")
    finally:
        session_running = False

# === Основной запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    asyncio.run(main())

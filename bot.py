from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from dotenv import load_dotenv
import logging
import os
import asyncio

# Загрузка переменных окружения
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Импортируем обработчики (где будет команда /start и остальная логика)
from handlers import register_handlers
register_handlers(dp)

async def main():
    print("✅ Bot is ready. Waiting for /start command.")
    # Не запускаем polling, чтобы бот не стартовал самовольно
    await asyncio.Event().wait()  # Просто ждёт, пока не получит сигнал

if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Dispatcher, types
from aiogram.types import Message

# Переменная, чтобы не запускать несколько сессий
session_active = False

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def start_handler(message: Message):
        global session_active
        if session_active:
            await message.answer("⚠️ Сессия уже запущена. Подожди завершения.")
            return

        session_active = True
        await message.answer("✅ Сессия запущена на 2 минуты...")

        # Здесь ваша торговая логика. Пока просто заглушка
        await message.answer("📊 (Тут будет запуск торговой стратегии)")

        # Подождать 2 минуты, потом завершить
        await asyncio.sleep(120)
        await message.answer("⏱ Сессия завершена.")
        session_active = False

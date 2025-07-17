from fastapi import FastAPI
import asyncio
import logging

from main import connect  # Импортируем WebSocket-цикл

app = FastAPI()
logging.basicConfig(level=logging.INFO)


@app.on_event("startup")
async def startup_event():
    logging.info("⏳ WebSocket запустится через 2 секунды...")
    await asyncio.sleep(2)

    # Запускаем connect в фоне
    asyncio.create_task(connect())

    # Планируем остановку через 2 минуты
    asyncio.create_task(stop_server_after_delay())


async def stop_server_after_delay():
    await asyncio.sleep(120)
    logging.info("🛑 Время вышло. Завершаем работу.")
    raise KeyboardInterrupt("Автоматическое завершение через 2 минуты.")


@app.get("/")
async def root():
    return {"message": "Бот работает. WebSocket активен."}


import asyncio
import time
from fastapi import FastAPI
from main import main  # Импортируем main из main.py

app = FastAPI()
last_run = 0  # Время последнего запуска

@app.get("/")
def root():
    return {"status": "Бот работает. Используйте /start для запуска."}

@app.get("/start")
async def start_bot():
    global last_run
    now = time.time()

    if last_run and now - last_run < 180:  # 3 минуты = 180 секунд
        return {"status": "⏳ Подождите 3 минуты перед следующим запуском."}

    last_run = now

    # Запускаем бота на 2 минуты
    async def run_with_timeout():
        task = asyncio.create_task(main())
        await asyncio.sleep(120)
        task.cancel()

    asyncio.create_task(run_with_timeout())
    return {"status": "✅ Бот запущен на 2 минуты. Ждите завершения."}

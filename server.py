from fastapi import FastAPI
import asyncio
from main import connect  # Импортируем WebSocket-цикл

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Бот работает. Используй /start для запуска"}

@app.get("/start")
async def start_bot():
    asyncio.create_task(connect())  # Запускаем connect в фоне
    return {"message": "Бот запущен на 2 минуты"}

# Эта часть нужна Railway, чтобы понять, что это веб-приложение
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080)

import os
import asyncio
from fastapi import FastAPI
from telegram_notifier import send_telegram_message
from websocket_client import connect_websocket as connect

app = FastAPI()

@app.get("/start")
async def handle_start():
    # 🔄 Запуск стратегии на 2 минуты
    asyncio.create_task(connect())

    # 🌐 Получаем домен проекта или задаём вручную
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "yourproject.up.railway.app")
    restart_link = f"https://{domain}/start"

    # 📬 Уведомление в Telegram
    await send_telegram_message(
        f"✅ <b>Процесс запущен на 2 минуты.</b>\n"
        f"🔁 Для нового запуска: <a href=\"{restart_link}\">{restart_link}</a>"
    )

    return {"message": "Asyncio работает"}

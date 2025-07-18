import os
import asyncio
from fastapi import FastAPI
from telegram_notifier import notify_telegram
from websocket_client import run_session

app = FastAPI()

@app.get("/start")
async def start_handler():
    # 🧠 Получаем домен Railway для создания restart-ссылки
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "yourproject.up.railway.app")
    restart_link = f"https://{domain}/start"

    # 🔄 Запускаем торговую сессию
    asyncio.create_task(run_session())

    # 📬 Уведомляем в Telegram
    await notify_telegram(
        f"🟢 <b>Процесс инициирован</b>\n"
        f"🔁 Ссылка для нового запуска: <a href=\"{restart_link}\">{restart_link}</a>"
    )

    return {"message": "Trading session started"}

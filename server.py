import asyncio
from fastapi import FastAPI
from telegram_notifier import send_telegram_message
from websocket_client import run_session

app = FastAPI()

@app.get("/start")
async def handle_start():
    # 🔄 Запуск стратегии на 2 минуты
    asyncio.create_task(run_session())

    # Заменяем переменную на явный домен
    restart_link = "https://tradebot-production-c405.up.railway.app/start"

    # 📬 Уведомление в Telegram
    await send_telegram_message(
        f"✅ <b>Процесс запущен на 2 минуты.</b>\n"
        f"🔁 Для нового запуска: <a href=\"{restart_link}\">{restart_link}</a>"
    )

    return {"message": "Strategy started"}

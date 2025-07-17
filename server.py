import os
import asyncio
from fastapi import FastAPI
#from telegram_notifier import send_telegram_message
#from client import connect

print("✅ server.py импортирован")

app = FastAPI()

@app.get("/start")
async def handle_start():
    print("🔄 /start endpoint вызван")

    asyncio.create_task(asyncio.sleep(1))
    
    return {"message":"Asyncio работает"}
    #asyncio.create_task(connect())

    # 🌐 Получаем домен проекта или задаём вручную
    #domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "yourproject.up.railway.app")
    #restart_link = f"https://{domain}/start"

    # 📬 Уведомление в Telegram
    #await send_telegram_message(
        #f"✅ <b>Процесс запущен на 2 минуты.</b>\n"
        #f"🔁 Для нового запуска: <a href=\"{restart_link}\">{restart_link}</a>"
    #)

    #return {"message": "Strategy started"}

import aiohttp
from aiohttp import web
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
import json

from websocket_client import run_session
from telegram_notifier import send_telegram_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

routes = web.RouteTableDef()

@routes.post(f"/{os.getenv('WEBHOOK_SECRET')}")
async def handle(request):
    try:
        print("⚠️ Webhook получен!")
        data = await request.json()
        print("🥚 Данные запроса:", data)

        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text == "/start":
            await send_telegram_message("▶️ Сессия запущена", chat_id)
            await run_session()
        
        return web.Response(text="Webhook handled")  # <= это завершает POST-хендлер

    except Exception as e:
        print("❌ Ошибка:", e)
        return web.Response(status=500, text="Internal Server Error")

# 🔧 Добавляем GET для проверки доступности сервера
@routes.get("/")
async def healthcheck(request):
    return web.Response(text="✅ Bot is alive!")

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    print(f"🚀 Сервер слушает путь: /{WEBHOOK_SECRET}")
    web.run_app(app, host="0.0.0.0", port=8080)

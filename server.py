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

@routes.post(f'/{WEBHOOK_SECRET}')
async def handle(request):
    try:
        print("⚠️ Webhook получен!")  # Лог
        data = await request.json()
        print("🍑 Данные запроса:", data)  # Лог

        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text == "/start":
            await send_telegram_message("🟢 Команда /start получена. Запускаю сессию...", chat_id)
            await run_session(duration_seconds=120)

    except Exception as e:
        print("❌ Ошибка в webhook обработчике:", e)
    return web.Response(text="OK")

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    print(f"🚀 Сервер слушает путь: /{WEBHOOK_SECRET}")
    web.run_app(app, host="0.0.0.0", port=8080)

import aiohttp
from aiohttp import web
import asyncio
import os
from dotenv import load_dotenv
import json

from websocket_client import run_session
from telegram_notifier import send_telegram_message

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

routes = web.RouteTableDef()

# Глобальный флаг — идёт ли сессия
is_session_running = False

@routes.post(f"/{WEBHOOK_SECRET}")
async def handle(request):
    global is_session_running

    try:
        data = await request.json()
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))

        # Проверка: только если текст "/start" и chat_id совпадает
        if text == "/start" and chat_id == CHAT_ID and not is_session_running:
            is_session_running = True
            await send_telegram_message("✅ Сессия запущена. Работаем 2 минуты...")
            await run_session(duration_seconds=120, chat_id=chat_id)
            await send_telegram_message("⏹️ Сессия завершена.")
            is_session_running = False

        return web.Response(status=200, text="ok")

    except Exception as e:
        print(f"❌ Ошибка в обработке webhook: {e}")
        return web.Response(status=500, text="error")

@routes.get("/")
async def health_check(request):
    return web.Response(text="Bot is alive")

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, port=port)

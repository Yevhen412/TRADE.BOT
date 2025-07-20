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
        print("📥 Webhook получен!")  # <-- ЛОГ
        data = await request.json()
        print("🍑 Данные запроса:", data)  # <-- ЛОГ

        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text == "/start":
            await send_telegram_message("🟢 Команда /start получена. Запускаю сессию на 120 секунд", chat_id)
            await run_session(duration_seconds=120)

        return web.Response(status=200, text="OK")
    except Exception as e:
        print(f"❌ Ошибка в webhook обработчике: {e}")
        return web.Response(status=500, text="Internal Server Error")

@routes.get('/')
async def health_check(request):
    return web.Response(text="✅ Bot is alive!")

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, port=port)

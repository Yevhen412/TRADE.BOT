import aiohttp
from aiohttp import web
import asyncio
import os
import json
from websocket_client import run_session
from telegram_notifier import send_telegram_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # например: mysecretpath

routes = web.RouteTableDef()

@routes.post(f'/{os.getenv("WEBHOOK_SECRET")}')
async def handle(request):
    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if text == "/start":
        await send_telegram_message("🟢 Команда /start получена. Запускаю сессию...")
        await run_session(duration_seconds=120)
    else:
        await send_telegram_message("🤖 Неизвестная команда.")

    return web.Response(text="OK")

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=8000)

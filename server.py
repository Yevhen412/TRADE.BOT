import aiohttp
from aiohttp import web
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
import json
from websocket_client import run_session
from telegram_notifier import send_telegram_message


BOT_TOKEN = "7588221701:AAF6M-RrXXlRN5_udNG-oQ2nC2rQoqbq7os"
WEBHOOK_SECRET = "startbot123"

routes = web.RouteTableDef()

@routes.post(f'/{os.getenv("WEBHOOK_SECRET")}')
async def handle(request):
    try:
        print("🔔 Webhook получен!")  # <-- ДОБАВЬ
        data = await request.json()
        print("📦 Данные запроса:", data)  # <-- ДОБАВЬ

        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text == "/start":
            await send_telegram_message("🟢 Команда /start получена. Запускаю сессию...")
            await run_session(duration_seconds=120)
        else:
            await send_telegram_message("🤖 Неизвестная команда.")
        
        return web.Response(text="OK")
    
    except Exception as e:
        print("❌ Ошибка в обработчике:", e)  # <-- ДОБАВЬ
        return web.Response(status=500, text="Internal Error")

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    print(f"🔧 Сервер слушает путь: /{WEBHOOK_SECRET}")
    web.run_app(app, port=8000)

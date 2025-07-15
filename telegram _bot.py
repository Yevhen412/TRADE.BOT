import os
import aiohttp
from aiohttp import web

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
BOT_ENABLED = True  # Флаг состояния

async def notify_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                resp_text = await response.text()
                print(f"[Telegram] Ответ: {resp_text}")
    except Exception as e:
        print("❌ Ошибка при отправке в Telegram:", e)

# ===========================
# ↓ Обработка команд Telegram ↓
# ===========================

routes = web.RouteTableDef()

@routes.post(f"/{BOT_TOKEN}")
async def handle_webhook(request):
    global BOT_ENABLED

    try:
        data = await request.json()
        message = data.get("message", {})
        chat_id = str(message.get("chat", {}).get("id"))
        text = message.get("text", "")

        if chat_id != CHAT_ID:
            return web.Response(text="⛔ Неверный chat_id")

        if text == "/start_bot":
            BOT_ENABLED = True
            await notify_telegram("▶️ Бот запущен вручную.")
        elif text == "/stop_bot":
            BOT_ENABLED = False
            await notify_telegram("⏸️ Бот остановлен вручную.")
        else:
            await notify_telegram("❓ Неизвестная команда.")

        return web.Response(text="OK")
    except Exception as e:
        print("Ошибка обработки команды:", e)
        return web.Response(status=500, text="Ошибка")

def get_app():
    app = web.Application()
    app.add_routes(routes)
    return app

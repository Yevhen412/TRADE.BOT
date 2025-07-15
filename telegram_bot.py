import os
import aiohttp
from aiohttp import web

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
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


def bot_should_run():
    return True


# ==============================
# Обработка команд Telegram ↓
# (можно позже реализовать, если нужно)

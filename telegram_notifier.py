import aiohttp
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN или CHAT_ID не заданы!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                response = await resp.json()
                print("📬 Telegram:", response)
    except Exception as e:
        print("Ошибка отправки в Telegram:", e)

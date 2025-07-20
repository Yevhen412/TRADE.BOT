import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_telegram_message(text):
    if not TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN или CHAT_ID не заданы.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print("❌ Ошибка при отправке сообщения:", resp.status)
    except Exception as e:
        print("❌ Ошибка соединения с Telegram:", e)

from dotenv import load_dotenv
import os
import asyncio
import aiohttp

load_dotenv(dotenv_path=".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ BOT_TOKEN или CHAT_ID не заданы.")

async def send_telegram_message(message: str):
    if not TOKEN or not CHAT_ID:
        print("❌ BOT_TOKEN или CHAT_ID не заданы.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                if resp.status != 200:
                    print("❌ Ошибка при отправке в Telegram:", await resp.text())
    except Exception as e:
        print("❌ Telegram ошибка:", e)

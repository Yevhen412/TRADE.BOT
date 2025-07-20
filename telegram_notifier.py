import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def send_telegram_message(text, chat_id):
    if not BOT_TOKEN or not chat_id:
        print("❌ BOT_TOKEN или chat_id не задан.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                response = await resp.json()
                print("✅ Ответ Telegram:", response)
                return response
    except Exception as e:
        print("❌ Ошибка при отправке сообщения:", e)

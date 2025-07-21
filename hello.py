"""
import os
import asyncio
import aiohttp

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("✅ Скрипт hello.py запущен")
print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

async def send():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🚀 Привет от hello.py"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as r:
            print("📨 Ответ Telegram:", await r.text())

asyncio.run(send())

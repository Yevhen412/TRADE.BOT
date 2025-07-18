import os
import aiohttp

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

async def notify_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials not set")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            if resp.status != 200:
                print(f"❌ Ошибка Telegram API: {resp.status}")
            else:
                print("✅ Отправлено в Telegram")

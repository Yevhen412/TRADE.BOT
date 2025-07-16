import os
import aiohttp

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

async def send_telegram_message(message: str):
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

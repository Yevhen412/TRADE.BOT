import os
import httpx

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

async def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Не заданы переменные TELEGRAM_BOT_TOKEN или CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            if response.status_code != 200:
                print(f"[ERROR] Telegram error: {response.text}")
    except Exception as e:
        print(f"[EXCEPTION] Ошибка при отправке Telegram-сообщения: {e}")

import os
import httpx

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return  # Безопасно молчать

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, data=payload)
            if response.status_code != 200:
                print(f"[TELEGRAM ERROR] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[TELEGRAM EXCEPTION] {e}")

import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    """
    Отправка сообщения в Telegram-чат.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Не заданы переменные окружения TELEGRAM_TOKEN или TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            print(f"[ERROR] Не удалось отправить сообщение в Telegram: {response.text}")
    except Exception as e:
        print(f"[EXCEPTION] Ошибка отправки Telegram-сообщения: {e}")

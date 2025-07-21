import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

async def send_telegram_message(text, chat_id):
    if not TOKEN or not chat_id:
        print("❌ BOT_TOKEN или chat_id не заданы.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                print(f"❌ Ошибка отправки сообщения: {response.status_code}")
                print("Ответ Telegram:", response.text)
            else:
                print("✅ Сообщение отправлено успешно")
    except Exception as e:
        print("❌ Исключение при отправке сообщения:", str(e))

import aiohttp
import os
import asyncio

async def send_telegram_message(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не установлены.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                if resp.status != 200:
                    print(f"❌ Ошибка отправки сообщения в Telegram: {resp.status}")
                    text = await resp.text()
                    print(text)
                else:
                    print("✅ Сообщение отправлено в Telegram.")
    except Exception as e:
        print(f"❌ Telegram send error: {e}")

# Пример ручного запуска:
if __name__ == "__main__":
    asyncio.run(send_telegram_message("🔔 Бот запущен и работает!"))

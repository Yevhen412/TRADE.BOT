import os
import asyncio
import aiohttp

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def test_send():
    print(f"[DEBUG] BOT_TOKEN: {BOT_TOKEN}")
    print(f"[DEBUG] CHAT_ID: {CHAT_ID}")
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения отсутствуют!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": "✅ Проверка отправки сообщения из Railway"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                print(f"📡 Статус ответа: {resp.status}")
                print(f"🔁 Ответ: {await resp.text()}")
    except Exception as e:
        print(f"🔥 Ошибка отправки: {e}")

if __name__ == "__main__":
    asyncio.run(test_send())

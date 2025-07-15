import asyncio
import aiohttp
import os

print("🚀 main.py точно запущен")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

print(f"📌 BOT_TOKEN: {repr(BOT_TOKEN)}")
print(f"📌 CHAT_ID: {repr(CHAT_ID)}")

async def send_telegram_message(text: str):
    print("📨 Отправка сообщения началась...")

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    print(f"📤 URL: {url}")
    print(f"📤 Payload: {payload}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                resp_text = await response.text()
                print("📬 Ответ Telegram:", resp_text)
    except Exception as e:
        print("❌ Ошибка при отправке:", e)

if __name__ == "__main__":
    print("📣 Вызов send_telegram_message...")
    asyncio.run(send_telegram_message("✅ Это тестовое сообщение от main.py"))

import asyncio
import os
from dotenv import load_dotenv
import httpx
from websocket_client import run_session
from telegram_notifier import send_telegram_message

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POLLING_INTERVAL = 2  # интервал опроса в секундах

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
is_session_running = False


async def get_updates(offset=None):
    params = {"timeout": 10, "offset": offset}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/getUpdates", params=params)
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка в get_updates: {e}")
            return {}


async def send_reply(chat_id, text):
    await send_telegram_message(text, chat_id)


async def polling_loop():
    global is_session_running
    last_update_id = None
    print("🤖 Бот запущен (polling)...")

    while True:
        try:
            updates = await get_updates(offset=last_update_id)
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = str(message.get("chat", {}).get("id", ""))
                text = message.get("text", "")

                if chat_id != CHAT_ID:
                    continue

                if text == "/start":
                    if is_session_running:
                        await send_reply(chat_id, "⏳ Уже идёт сессия...")
                    else:
                        is_session_running = True
                        await send_reply(chat_id, "✅ Сессия запущена. Работаем 2 минуты...")
                        await run_session(chat_id=chat_id, duration_seconds=120)
                        await send_reply(chat_id, "⏹️ Сессия завершена.")
                        is_session_running = False

            await asyncio.sleep(POLLING_INTERVAL)

        except Exception as e:
            print(f"❌ Ошибка в polling_loop: {e}")
            await asyncio.sleep(5)


async def main():
    try:
        await polling_loop()
    except Exception as e:
        print(f"❌ Ошибка в main: {e}")
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())

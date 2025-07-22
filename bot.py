import asyncio
import os
from dotenv import load_dotenv
from telegram_notifier import send_telegram_message
from websocket_client import connect_websocket

import httpx  # ОБЯЗАТЕЛЬНО!

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

is_session_running = False


async def get_updates(offset=None):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}?timeout=10&offset={offset}")
            return resp.json()
    except httpx.ReadTimeout:
        print("⚠️ ReadTimeout при попытке получить обновления от Telegram")
        return {}


async def polling_loop():
    global is_session_running
    last_update_id = None
    print("🤖 Бот готов. Ждёт команду /start...")

    while True:
        try:
            updates = await get_updates(offset=last_update_id)
        except Exception as e:
            print("[Telegram ERROR]", e)
            await send_telegram_message(f"❗Ошибка при получении обновлений:\n{e}")
            await asyncio.sleep(5)
            continue

        if "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    text = update["message"]["text"]
                    chat_id = update["message"]["chat"]["id"]

                    if text == "/start" and str(chat_id) == TELEGRAM_CHAT_ID:
                        if not is_session_running:
                            is_session_running = True
                            print("🚀 Сессия началась!")
                            await send_telegram_message("🚀 Сессия запущена! Бот работает 2 минуты.")
                            asyncio.create_task(run_session())
                        else:
                            await send_telegram_message("⚠️ Сессия уже запущена.")
        await asyncio.sleep(1)


async def run_session():
    global is_session_running
    await connect_websocket()
    await asyncio.sleep(120)  # 2 минуты
    is_session_running = False
    await send_telegram_message("✅ Сессия завершена. Ждёт команду /start.")
    print("🛑 Сессия завершена.")


if __name__ == "__main__":
    asyncio.run(polling_loop())

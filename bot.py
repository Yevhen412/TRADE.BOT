import asyncio
import os
from dotenv import load_dotenv
from telegram_notifier import send_telegram_message
import websocket_client

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
is_session_running = False

async def get_updates(offset=None):
    import httpx
    params = {"timeout": 10, "offset": offset}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_URL}/getUpdates", params=params)
        return resp.json()

async def polling_loop():
    global is_session_running
    last_update_id = None
    print("🤖 Бот готов. Ждёт команду /start...")

    while True:
        try:
    updates = await get_updates(offset=last_update_id)
except Exception as e:
    print("[Telegram ERROR]", e)
    await send_telegram_message(f"❗️Ошибка при получении обновлений от Telegram:\n{e}")
    await asyncio.sleep(5)
    continue
        if "result" in updates:
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                if "message" in update:
                    text = update["message"].get("text", "")
                    chat_id = update["message"]["chat"]["id"]

                    if text == "/start" and not is_session_running:
                        is_session_running = True
                        await send_telegram_message("✅ Сессия запущена на 2 минуты…")
                        await websocket_client.connect_websocket(duration_seconds=120)
                        await send_telegram_message("🛑 Сессия завершена. Торговля остановлена.")
                        is_session_running = False

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(polling_loop())

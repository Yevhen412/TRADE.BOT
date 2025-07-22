import asyncio
import os
from dotenv import load_dotenv
from telegram_notifier import send_telegram_message
from websocket_client import connect_websocket

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
        updates = await get_updates(offset=last_update_id)
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            message = update.get("message", {})
            chat_id = str(message.get("chat", {}).get("id", ""))
            text = message.get("text", "")

            if chat_id != TELEGRAM_CHAT_ID:
                continue

            if text == "/start":
                if is_session_running:
                    await send_telegram_message("⚠️ Уже запущена сессия.")
                    continue

                is_session_running = True
                await send_telegram_message("✅ Сессия запущена на 2 минуты.")
                await connect_websocket(duration_seconds=120)
                await send_telegram_message("⏹️ Сессия завершена.")
                is_session_running = False

        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(polling_loop())

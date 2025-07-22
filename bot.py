import asyncio
import os
import httpx
from dotenv import load_dotenv
from telegram_notifier import send_telegram_message
import websocket_client

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
is_session_running = False

async def get_updates(offset=None):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}/getUpdates", params={"offset": offset})
            return resp.json()
    except httpx.ReadTimeout:
        print("⚠️ ReadTimeout при попытке получить обновления Telegram")
        return {}  # Возвращаем пустой словарь, чтобы не упало в polling_loop

async def polling_loop():
    global is_session_running
    last_update_id = None
    print("🤖 Бот готов. Ждёт команду /start...")

    while True:
        try:
            updates = await get_updates(offset=last_update_id)
        except Exception as e:
            print("[Telegram ERROR]", e)
            await send_telegram_message(f"❗Ошибка при получении обновлений: {e}")
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
                            await send_telegram_message("✅ Торговая сессия запущена!")
                            await websocket_client.connect_websocket()
                            is_session_running = False
                            await send_telegram_message("⏹ Торговая сессия завершена.")
                        else:
                            await send_telegram_message("⚠ Сессия уже запущена.")

        await asyncio.sleep(5)  # ← вот здесь обязательно!
        
if __name__ == "__main__":
    asyncio.run(polling_loop())

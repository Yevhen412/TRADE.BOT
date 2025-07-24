import asyncio
import time
import httpx
import os
from telegram_notifier import send_telegram_message
from websocket_client import connect_websocket

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LAST_UPDATE_ID = None
active_session = False
last_start_time = 0

async def check_for_start_command():
    global LAST_UPDATE_ID, active_session, last_start_time

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(url, params={"offset": LAST_UPDATE_ID + 1 if LAST_UPDATE_ID else None})
                data = response.json()

                if data["ok"]:
                    for result in data["result"]:
                        LAST_UPDATE_ID = result["update_id"]

                        if "message" in result and "text" in result["message"]:
                            text = result["message"]["text"]
                            if text == "/start":
                                now = time.time()
                                if active_session:
                                    await send_telegram_message("⚠️ Сессия уже активна.")
                                elif now - last_start_time < 180:
                                    await send_telegram_message("⏳ Подождите немного перед следующим запуском.")
                                else:
                                    active_session = True
                                    last_start_time = now
                                    await send_telegram_message("🚀 Запуск торговой сессии...")
                                    await connect_websocket(duration_seconds=120)
                                    await send_telegram_message("🛑 Сессия завершена.")
                                    active_session = False

                await asyncio.sleep(2)

            except Exception as e:
                print(f"[ERROR] Telegram polling: {e}")
                await asyncio.sleep(5)

async def main():
    await send_telegram_message("🤖 Бот запущен. Жду команду /start.")
    await check_for_start_command()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Остановка вручную.")

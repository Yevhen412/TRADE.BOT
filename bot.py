import asyncio
from telegram_notifier import send_telegram_message
from connect_websocket import connect_websocket

active_session = False

async def main():
    global active_session

    if active_session:
        print("❗️Сессия уже активна.")
        return

    active_session = True
    try:
        print("🚀 Запуск WebSocket-сессии...")
        await connect_websocket(duration_seconds=120)
    finally:
        active_session = False
        print("🛑 Сессия завершена.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Остановка вручную.")

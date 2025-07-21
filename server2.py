"""
import asyncio
from dotenv import load_dotenv
import os

from websocket_client import run_session
from telegram_notifier import send_telegram_message
from aiohttp import web

load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")

async def main():
    await send_telegram_message("✅ Сессия запущена. Работаем 2 минуты...")
    await run_session(duration_seconds=120, chat_id=CHAT_ID)
    await send_telegram_message("⏹️ Сессия завершена.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, port=port)

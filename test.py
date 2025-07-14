import asyncio
import aiohttp
import os
from trade_simulator import TradeSimulator

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip().lstrip('=')
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

simulator = TradeSimulator()

async def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    # 🔍 Отладочный вывод
    print(f"[DEBUG] BOT_TOKEN: '{BOT_TOKEN}'")
    print(f"[DEBUG] CHAT_ID: '{CHAT_ID}'")
    print(f"[DEBUG] URL: '{url}'")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            print("📩 Ответ Telegram:", await response.text())


if __name__ == "__main__":
    print("🚀 Запуск бота...")
    asyncio.run(send_telegram_message("✅ Бот успешно запущен!"))

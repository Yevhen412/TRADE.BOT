import asyncio
import os
import aiohttp
from trade_simulator import TradeSimulator

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BOT_ENABLED = True

simulator = TradeSimulator()

async def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            print("✅ Ответ Telegram:", await response.text())

# ⬇️ Это добавь в самый конец
if __name__ == "__main__":
    print("🚀 Запуск бота...")
    asyncio.run(send_telegram_message("🤖 Бот успешно запущен!"))

import asyncio
import os
import aiohttp
from trade_simulator import TradeSimulator

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
BOT_ENABLED = True

simulator = TradeSimulator()

async def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return

    # 🔧 Убедимся, что переменные без лишних символов
    token = BOT_TOKEN.strip()
    chat_id = CHAT_ID.strip()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    # ✅ Отладочный вывод
    print(f"[DEBUG] BOT_TOKEN: '{token}'")
    print(f"[DEBUG] CHAT_ID: '{chat_id}'")
    print(f"[DEBUG] URL: {url}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            print("✅ Ответ Telegram:", await response.text())

# ⬇️ Это добавь в самый конец
if __name__ == "__main__":
    print("🚀 Запуск бота...")
    asyncio.run(send_telegram_message("🤖 Бот успешно запущен!"))

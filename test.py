import asyncio
import aiohttp
import os
from trade_simulator import TradeSimulator

# 🚀 Отладка переменных окружения при загрузке
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

simulator = TradeSimulator()

async def send_telegram_message(text: str):
    print("📨 Пытаемся отправить сообщение...")

    # 🔍 Проверка переменных
    print("🔍 BOT_TOKEN:", repr(BOT_TOKEN))
    print("🔍 CHAT_ID:", repr(CHAT_ID))

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                resp_text = await response.text()
                print("📩 Ответ Telegram:", resp_text)
    except Exception as e:
        print("❌ Ошибка при отправке сообщения:", e)

if __name__ == "__main__":
    print("🚀 test.py запущен")
    asyncio.run(send_telegram_message("✅ Бот успешно запущен!"))

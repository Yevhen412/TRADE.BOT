import asyncio
import aiohttp
import os

# Импорт симулятора, если нужен
from trade_simulator import TradeSimulator

# Получаем переменные окружения и очищаем от пробелов и символов =
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip().lstrip("=")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

simulator = TradeSimulator()  # если используется

async def send_telegram_message(text: str):
    print("🟡 [DEBUG] Вызвана send_telegram_message()")

    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        print(f"[DEBUG] BOT_TOKEN: '{BOT_TOKEN}'")
        print(f"[DEBUG] CHAT_ID: '{CHAT_ID}'")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    # Отладка
    print(f"[DEBUG] BOT_TOKEN: '{BOT_TOKEN}'")
    print(f"[DEBUG] CHAT_ID: '{CHAT_ID}'")
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] PAYLOAD: {payload}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                response_text = await response.text()
                print("📩 Ответ Telegram:", response.status, response_text)
    except Exception as e:
        print("❌ Ошибка при отправке сообщения:", str(e))


if __name__ == "__main__":
    print("🚀 Запуск бота...")
    asyncio.run(send_telegram_message("✅ Бот успешно запущен!"))

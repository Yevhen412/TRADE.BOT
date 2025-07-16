import asyncio
import aiohttp
import os
import json
from trade_simulator import TradeSimulator

print("🚀 main.py точно запущен")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

simulator = TradeSimulator()

async def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                print("📬 Telegram:", await resp.text())
    except Exception as e:
        print("❌ Ошибка Telegram:", e)

async def subscribe_to_ws():
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "ADAUSDT"]
    topics = [f"publicTrade.{pair}" for pair in pairs]

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            print("🌐 Подключено к WebSocket")

            await ws.send_json({
                "op": "subscribe",
                "args": topics
            })

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        event = json.loads(msg.data)
                        signal = simulator.process(event)
                        if signal:
                            message = simulator.simulate_trade(signal)
                            if message:
                                await send_telegram_message(message)
                    except Exception as e:
                        print("❌ Ошибка обработки сообщения:", e)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("❌ Ошибка WebSocket:", msg)
                    break

# 🔁 Вечный цикл с авто-переподключением
async def main():
    while True:
        try:
            await subscribe_to_ws()
        except Exception as e:
            print("❌ Общая ошибка в WebSocket-сессии:", e)
        print("🔁 Переподключение через 5 секунд...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

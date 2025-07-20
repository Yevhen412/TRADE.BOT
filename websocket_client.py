
import asyncio
import json
import time
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

async def connect_websocket(simulator, chat_id, duration_seconds=120):
    print("🌐 Подключаюсь к WebSocket")
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "ADAUSDT"]
    topics = [f"publicTrade.{pair}" for pair in pairs]

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            await ws.send_json({
                "op": "subscribe",
                "args": topics
            })
            print("✅ Подписка завершена")
            start = time.time()

            while time.time() - start < duration_seconds:
                try:
                    msg = await ws.receive()
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        event = json.loads(msg.data)
                        signal = simulator.process(event)
                        if signal:
                            message = await simulator.execute_trade(signal)
                            if message:
                                await send_telegram_message(message, chat_id)
                except Exception as e:
                    print("❌ Ошибка WebSocket:", e)
                    break

async def run_session(chat_id, duration_seconds=120):
    print("🔁 Запуск сессии на", duration_seconds, "секунд")
    simulator = TradeSimulator()  # создаём только внутри сессии
    await send_telegram_message("🚀 Сессия началась", chat_id)
    await connect_websocket(simulator, chat_id, duration_seconds)
    print("📊 Получаю финальный отчет")
    report = simulator.get_session_pnl_report()
    await send_telegram_message(report, chat_id)
    print("✅ Сессия завершена")

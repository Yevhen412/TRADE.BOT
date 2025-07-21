import asyncio
import json
import time
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

async def connect_websocket(simulator, chat_id, duration_seconds=120):
    print("🌐 Подключаюсь к WebSocket")
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "ADAUSDT"]
    topics = [f"publicTrade.{pair}" for pair in pairs]

    try:
        async with websockets.connect(url) as ws:
            subscribe_msg = json.dumps({
                "op": "subscribe",
                "args": topics
            })
            await ws.send(subscribe_msg)
            print("✅ Подписка завершена")
            start = time.time()

            while time.time() - start < duration_seconds:
                try:
                    msg = await ws.recv()
                    event = json.loads(msg)
                    signal = simulator.process(event)
                    if signal:
                        message = await simulator.execute_trade(signal)
                        if message:
                            await send_telegram_message(message, chat_id)
                except Exception as e:
                    print("❌ Ошибка WebSocket:", e)
                    break
    except Exception as e:
        print("❌ Ошибка подключения к WebSocket:", e)

async def run_session(chat_id, duration_seconds=120):
    print("🔁 Запуск сессии на", duration_seconds, "секунд")
    simulator = TradeSimulator()
    await send_telegram_message("🚀 Сессия началась", chat_id)
    await connect_websocket(simulator, chat_id, duration_seconds)
    report = simulator.get_session_pnl_report()
    await send_telegram_message(report, chat_id)
    print("✅ Сессия завершена")

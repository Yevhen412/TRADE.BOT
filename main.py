import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

async def connect():
    uri = "wss://stream.bybit.com/v5/public/spot"
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "ADAUSDT"]
    topics = [f"publicTrade.{pair}" for pair in pairs]

    while True:
        try:
            print("🔌 Подключаемся к WebSocket...")
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({
                    "op": "subscribe",
                    "args": topics
                }))
                print("✅ Подписка завершена")

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)

                    if message.get("type") == "snapshot":
                        continue

                    signal = simulator.process(message)

                    if signal:
                        print("📈 Получен сигнал, симулируем сделку...")
                        report = simulator.simulate_trade(signal)

                        if report:
                            print("📬 Отправляем сообщение в Telegram...")
                            await send_telegram_message(report)
                        else:
                            print("📭 Сделка без прибыли, Telegram не уведомляется.")
        except Exception as e:
            print(f"❌ Ошибка WebSocket: {e}")
            print("⏳ Повторное подключение через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("🚀 main.py запущен")
    asyncio.run(connect())

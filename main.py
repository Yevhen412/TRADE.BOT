import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

async def connect():
    uri = "wss://stream.bybit.com/v5/public/spot"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({
                    "op": "subscribe",
                    "args": [
                        "publicTrade.BTCUSDT",
                        "publicTrade.ETHUSDT",
                        "publicTrade.XRPUSDT",
                        "publicTrade.SOLUSDT",
                        "publicTrade.ADAUSDT",
                        "publicTrade.AVAXUSDT"
                    ]
                }))
                print("✅ WebSocket подписка завершена")

                while True:
                    try:
                        response = await websocket.recv()
                        message = json.loads(response)

                        if message.get("type") == "snapshot":
                            continue

                        signal = simulator.process(message)
                        if signal:
                            report = simulator.simulate_trade(signal)
                            if report:
                                await send_telegram_message(report)

                    except websockets.ConnectionClosed:
                        print("🔁 WebSocket отключён. Повторное подключение через 5 секунд...")
                        break  # выйдет из вложенного while и переподключится
                    except Exception as e:
                        print("⚠️ Ошибка в обработке данных:", e)
                        await asyncio.sleep(3)

        except Exception as e:
            print("❌ Ошибка при подключении к WebSocket:", e)
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print("🛑 Остановка по Ctrl+C")
    except Exception as e:
        print("🔥 Критическая ошибка:", e)

import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message
from server import run_server  # aiohttp-сервер

simulator = TradeSimulator()

async def connect():
    print("📡 Подключаюсь к WebSocket...")
    uri = "wss://stream.bybit.com/v5/public/spot"
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
        print("✅ Подписка завершена")

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

            except Exception as e:
                print("🚨 Ошибка в WebSocket loop:", e)
                await asyncio.sleep(5)

if __name__ == "__main__":
    print("🚀 main.py запущен")
    loop = asyncio.get_event_loop()
    loop.create_task(connect())
    loop.run_in_executor(None, run_server)  # сервер работает параллельно
    loop.run_forever()

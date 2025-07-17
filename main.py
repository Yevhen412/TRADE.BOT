import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

async def main():
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
        print("✅ WebSocket подписка завершена")

        start_time = asyncio.get_event_loop().time()

        while True:
            if asyncio.get_event_loop().time() - start_time > 120:
                print("⏹️ Время работы истекло (2 минуты), останавливаемся.")
                break

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
                print("Ошибка в WebSocket loop:", e)
                await asyncio.sleep(5)

import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

async def connect():  # Функция экспортируется в telegram_server
    url = "wss://stream.bybit.com/v5/public/spot"
    async with websockets.connect(url) as websocket:
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
                print("❌ Ошибка в WebSocket loop:", e)
                await asyncio.sleep(5)

# Убираем запуск по умолчанию — теперь бот запускается через команду /start

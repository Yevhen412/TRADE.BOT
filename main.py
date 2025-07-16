import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message
from server import create_app  # изменим run_server на create_app
from aiohttp import web

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

async def heartbeat():
    while True:
        await send_telegram_message("💓 Я жив")
        await asyncio.sleep(600)  # каждые 10 минут

async def main():
    print("🚀 main.py запущен")

    # Параллельные задачи
    tasks = [
        connect(),
        heartbeat()
    ]

    # Запускаем aiohttp-сервер
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8000)
    await site.start()

    # Параллельно выполняем задачи
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import websockets
from aiohttp import web

from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message
from server import create_app  # Твой server.py уже содержит эту функцию

simulator = TradeSimulator()

# Фоновая задача WebSocket
async def websocket_loop():
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
                print("❌ Ошибка в WebSocket loop:", e)
                await asyncio.sleep(5)

# Задача «Я жив» каждые 10 минут
async def heartbeat_loop():
    while True:
        await send_telegram_message("🤖 Я жив! Бот работает.")
        await asyncio.sleep(600)  # 10 минут

# Подключаем задачи при старте
async def start_background_tasks(app):
    app['ws_task'] = asyncio.create_task(websocket_loop())
    app['heartbeat_task'] = asyncio.create_task(heartbeat_loop())

# Чистим задачи при остановке
async def cleanup_background_tasks(app):
    app['ws_task'].cancel()
    app['heartbeat_task'].cancel()
    await asyncio.gather(app['ws_task'], app['heartbeat_task'], return_exceptions=True)

# Объединённое приложение
def create_combined_app():
    app = create_app()
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    return app

if __name__ == "__main__":
    web.run_app(create_combined_app(), port=8000)

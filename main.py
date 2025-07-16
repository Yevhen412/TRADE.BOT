import asyncio
import json
import os
import websockets
from aiohttp import web
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

# ✅ WebSocket подписка на Bybit
async def connect():
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

        while True:
            try:
                message = json.loads(await websocket.recv())
                signal = simulator.process(message)
                if signal:
                    report = simulator.simulate_trade(signal)
                    if report:
                        await send_telegram_message(report)
            except Exception as e:
                print("❌ Ошибка WebSocket:", e)
                await asyncio.sleep(5)

# ✅ Периодическое сообщение "Я жив"
async def send_heartbeat():
    while True:
        await send_telegram_message("✅ Я жив. Бот активен.")
        await asyncio.sleep(600)

# ✅ HTTP-сервер для Railway ("/" → OK)
async def handle(request):
    return web.Response(text="✅ Bot is running")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8000)
    await site.start()
    print("🌐 HTTP-сервер запущен на порту 8000")

# ✅ Главная точка запуска
async def main():
    print("🚀 main.py запущен")
    await start_server()
    asyncio.create_task(send_heartbeat())
    await connect()  # главный бесконечный процесс — блокирует завершение

if __name__ == "__main__":
    asyncio.run(main())

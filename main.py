import asyncio
import json
import websockets
import time
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message, BOT_TOKEN, CHAT_ID

simulator = TradeSimulator()

running = False
last_run_time = 0
MIN_INTERVAL = 180  # 3 минуты между запусками

async def handle_command():
    global running, last_run_time
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    async with websockets.connect("wss://echo.websocket.org") as _:
        while True:
            try:
                async with asyncio.timeout(3):
                    async with websockets.connect("wss://stream.bybit.com/v5/public/spot") as ws:
                        await ws.send(json.dumps({
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
                        print("✅ Подписка на WebSocket завершена")

                        start_time = time.time()
                        while time.time() - start_time < 120:  # Работает 2 минуты
                            try:
                                message = await ws.recv()
                                data = json.loads(message)
                                if data.get("type") == "snapshot":
                                    continue

                                signal = simulator.process(data)
                                if signal:
                                    report = simulator.simulate_trade(signal)
                                    if report:
                                        await send_telegram_message(report)

                            except Exception as e:
                                print("Ошибка в loop:", e)
                                await asyncio.sleep(5)
            except:
                await asyncio.sleep(2)

async def polling_loop():
    global running, last_run_time
    print("🟡 Ожидание команды /start...")

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    updates = await resp.json()
                    if "result" in updates:
                        for update in updates["result"]:
                            msg = update.get("message", {})
                            if msg.get("text") == "/start":
                                now = time.time()
                                if running:
                                    await send_telegram_message("⏱ Бот уже запущен!")
                                elif now - last_run_time < MIN_INTERVAL:
                                    await send_telegram_message("⚠️ Подожди 3 минуты перед новым запуском.")
                                else:
                                    await send_telegram_message("✅ Бот запускается на 2 минуты...")
                                    last_run_time = now
                                    running = True
                                    await handle_command()
                                    running = False
                                    await send_telegram_message("⏹ Работа завершена. Ждём новую команду.")
            await asyncio.sleep(5)
        except Exception as e:
            print("Ошибка в polling:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(polling_loop())

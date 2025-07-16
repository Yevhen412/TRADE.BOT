import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

# 🔁 Пульс раз в 10 минут
async def heartbeat():
    while True:
        try:
            await send_telegram_message("🤖 Бот активен и слушает рынок...")
            print("💓 Heartbeat отправлен")
        except Exception as e:
            print("⚠️ Ошибка heartbeat:", e)
        await asyncio.sleep(600)  # 10 минут

# 📡 Основной WebSocket-процесс
async def run_bot():
    uri = "wss://stream.bybit.com/v5/public/spot"
    while True:
        try:
            print("🔌 Подключаюсь к WebSocket...")
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
                        print("🔁 WebSocket отключён. Переподключение...")
                        break
                    except Exception as e:
                        print("⚠️ Ошибка в обработке сообщения:", e)
                        await asyncio.sleep(3)
        except Exception as e:
            print("❌ Ошибка подключения к WebSocket:", e)
            await asyncio.sleep(10)

# 🧠 Запуск
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.create_task(heartbeat())  # 💓 Добавляем пульс!
    print("🚀 Бот запущен. Ожидание событий...")
    loop.run_forever()

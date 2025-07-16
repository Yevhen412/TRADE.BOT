import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

async def run_ws_session():
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
        print("✅ Подписка на WebSocket завершена")

        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=20)  # защита от замирания
                message = json.loads(response)

                if message.get("type") == "snapshot":
                    continue

                signal = simulator.process(message)
                if signal:
                    report = simulator.simulate_trade(signal)
                    if report:
                        await send_telegram_message(report)

            except asyncio.TimeoutError:
                print("⏱️ Таймаут: нет сообщений 20 секунд. Переподключение...")
                break
            except Exception as e:
                print("❌ Ошибка WebSocket:", e)
                break


async def main_loop():
    while True:
        try:
            await run_ws_session()
        except Exception as e:
            print("❌ Ошибка в main_loop:", e)
        print("🔁 Переподключение через 5 секунд...\n")
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main_loop())

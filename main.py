import asyncio
import json
import websockets
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()

is_running = False  # состояние запущен/остановлен

async def trading_cycle():
    global is_running
    is_running = True

    uri = "wss://stream.bybit.com/v5/public/spot"
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
            await send_telegram_message("✅ WebSocket подписан и активен на 2 минуты")

            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 120:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    message = json.loads(response)
                    if message.get("type") == "snapshot":
                        continue

                    signal = simulator.process(message)
                    if signal:
                        report = simulator.simulate_trade(signal)
                        if report:
                            await send_telegram_message(report)
                except asyncio.TimeoutError:
                    print("⏳ Таймаут ожидания данных")
                except Exception as e:
                    print("❌ Ошибка в торговом цикле:", e)
                    break
    except Exception as e:
        print("❌ Ошибка подключения к WebSocket:", e)
    finally:
        is_running = False
        print("🛑 Сессия завершена. Ожидается новая команда /start или переход по ссылке.")

if __name__ == "__main__":
    asyncio.run(trading_cycle())


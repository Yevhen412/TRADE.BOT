import asyncio
import json
import websockets

from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()


# Основной WebSocket-обработчик
async def connect():
    uri = "wss://stream.bybit.com/v5/public/spot"  # пример WebSocket-ссылки
    try:
        async with websockets.connect(uri) as websocket:
            subscribe_msg = {
                "op": "subscribe",
                "args": ["publicTrade.BTCUSDT"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            await send_telegram_message("✅ WebSocket подключен и подписан")

            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    # здесь можно добавить обработку данных
                    await simulator.handle_message(data)

                except Exception as inner_error:
                    await send_telegram_message(f"⚠️ Ошибка обработки сообщения: {inner_error}")
    except Exception as outer_error:
        await send_telegram_message(f"❌ Ошибка подключения: {outer_error}")


# Защита от автозапуска при импорте
if __name__ == "__main__":
    asyncio.run(connect())

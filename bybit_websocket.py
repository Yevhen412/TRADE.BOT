import asyncio
import websockets
import json

class BybitWebSocket:
    def __init__(self):
        self.url = "wss://stream.bybit.com/v5/public/spot"
        self.symbols = [
            "BTCUSDT", "ETHUSDT",
            "SOLUSDT", "AVAXUSDT",
            "XRPUSDT", "ADAUSDT"
        ]

    async def listen(self):
        async with websockets.connect(self.url) as ws:
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"publicTrade.{symbol}" for symbol in self.symbols]
            }
            await ws.send(json.dumps(subscribe_msg))

            while True:
                message = await ws.recv()
                try:
                    data = json.loads(message)
                    yield data
                except Exception as e:
                    print("Ошибка при обработке сообщения:", e)

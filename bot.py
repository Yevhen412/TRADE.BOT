import asyncio import os import json import time import hmac import hashlib import aiohttp from urllib.parse import urlencode

from telegram_notifier import send_telegram_message

all = ["connect_websocket"]

API_KEY = os.getenv("BYBIT_API_KEY") API_SECRET = os.getenv("BYBIT_API_SECRET")

session_active = True

def generate_signature(params: dict) -> str: query_string = urlencode(params) return hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

async def connect_websocket(duration_seconds=120): global session_active session_active = True url = "wss://stream.bybit.com/v5/public/spot" pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT"] end_time = time.time() + duration_seconds

async with aiohttp.ClientSession() as session:
    async with session.ws_connect(url) as ws:
        await ws.send_json({
            "op": "subscribe",
            "args": [f"tickers.{pair}" for pair in pairs]
        })

        try:
            while time.time() < end_time and session_active:
                msg = await ws.receive(timeout=10)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if 'data' in data:
                        symbol = data['data']['symbol']
                        price = data['data']['lastPrice']
                        print(f"[TICK] {symbol}: {price}")

            await send_telegram_message("✅ WebSocket сессия завершена.")
        except Exception as e:
            await send_telegram_message(f"❌ Ошибка WebSocket: {e}")

        await ws.close()
        session_active = False


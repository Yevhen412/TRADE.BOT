import asyncio
import websockets
import hmac
import hashlib
import json
import time
import os
import requests

from telegram_notifier import send_telegram_message

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

symbols = ["BTCUSDT", "ETHUSDT", "AVAXUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
price_data = {symbol: [] for symbol in symbols}
last_trade_time = 0
session_active = True

def get_timestamp():
    return int(time.time() * 1000)

def sign_request(secret, params):
    sorted_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(
        secret.encode('utf-8'),
        sorted_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

async def place_spot_order(symbol, quote_qty):
    url = "https://api.bybit.com/v5/order/create"
    timestamp = get_timestamp()

    body = {
        "category": "spot",
        "symbol": symbol,
        "side": "Buy",
        "orderType": "Market",
        "quoteQty": quote_qty,
        "orderLinkId": f"long_{timestamp}",
        "recvWindow": 5000,
        "timestamp": timestamp
    }

    signature = sign_request(API_SECRET, body)

    headers = {
        "Content-Type": "application/json",
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        res = response.json()
        if res.get("retCode") == 0:
            await send_telegram_message(f"✅ Успешная покупка {symbol}")
        else:
            await send_telegram_message(f"❌ Ошибка покупки {symbol}: {res}")
    except Exception as e:
        await send_telegram_message(f"❌ Исключение при покупке {symbol}: {e}")

async def process_message(message):
    global last_trade_time

    data = json.loads(message)
    if "data" not in data or "s" not in data["data"]:
        return

    symbol = data["data"]["s"]
    price = float(data["data"]["p"])
    price_data[symbol].append(price)

    print(f"[TICK] {symbol}: {price}")

    if time.time() - last_trade_time < 5:
        return

    if all(len(price_data[s]) > 0 for s in symbols):
        # Пример: простейшая логика корреляции по ETHUSDT
        eth_price = price_data["ETHUSDT"][-1]
        sol_price = price_data["SOLUSDT"][-1]

        # Простая проверка расхождения
        if abs(eth_price - sol_price) > 0.3:
            await send_telegram_message(f"[SIGNAL] Correlation found: ETHUSDT")
            last_trade_time = time.time()
            await place_spot_order("ETHUSDT", 200)

async def connect_websocket(duration_seconds=120):
    global session_active
    session_active = True
    url = "wss://stream.bybit.com/v5/public/spot"

    async with websockets.connect(url) as ws:
        subscribe_msg = {
            "op": "subscribe",
            "args": [f"publicTrade.{symbol}" for symbol in symbols]
        }
        await ws.send(json.dumps(subscribe_msg))
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=30)
                await process_message(message)
            except asyncio.TimeoutError:
                print("⚠️ Timeout. Повторная попытка получения сообщения.")
                continue
            except Exception as e:
                print(f"❌ Ошибка WebSocket: {e}")
                await send_telegram_message(f"❌ Ошибка WebSocket: {e}")
                break

        await send_telegram_message("✅ WebSocket сессия завершена.")
        session_active = False

__all__ = ["connect_websocket"]

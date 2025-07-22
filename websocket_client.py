import time
import json
import os
import asyncio
import websockets
import httpx
from dotenv import load_dotenv
from telegram_notifier import send_telegram_message

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

SYMBOL_GROUPS = [["ETHUSDT", "BTCUSDT"], ["SOLUSDT", "AVAXUSDT"], ["XRPUSDT", "ADAUSDT"]]
TRADE_SIZE = 200
COMMISSION_RATE = 0.0028  # 0.28%
MIN_PROFIT = 0.03
STOP_LOSS_MULTIPLIER = 1 / 2.25
TRADE_INTERVAL = 5

last_trade_time = 0
in_trade = False

def process_event(event):
    # 💡 Здесь будет логика сигнала. Пока фиктивно:
    now = time.time()
    global last_trade_time, in_trade
    if in_trade or now - last_trade_time < TRADE_INTERVAL:
        return None
    in_trade = True
    last_trade_time = now
    return {
        "symbol": "ETHUSDT",
        "entry_price": 2000.0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

async def place_spot_order(symbol, side, qty):
    url = "https://api.bybit.com/v5/order/create"
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "category": "spot",  # Вариант: удалить это поле, если UNIFIED
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": qty,
        "timeInForce": "IOC"
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            data = resp.json()
            if "retCode" in data and data["retCode"] == 0:
                return data
            else:
                await send_telegram_message(f"❌ Не удалось купить {symbol}: {data.get('retMsg', 'Unknown error')}")
    except Exception as e:
        await send_telegram_message(f"❌ Ошибка при покупке {symbol}: {str(e)}")
    return None

async def execute_trade(signal):
    global in_trade
    symbol = signal["symbol"]
    entry_price = signal["entry_price"]
    take_price = round(entry_price * 1.0045, 2)
    stop_price = round(entry_price * (1 - (1.0045 - 1) / 2.25), 2)

    result = await place_spot_order(symbol, "Buy", qty=TRADE_SIZE / entry_price)
    if result:
        await send_telegram_message(
            f"✅ ЖИВАЯ СДЕЛКА: Куплено {symbol} по {entry_price}, тейк {take_price}, стоп {stop_price}"
        )
    in_trade = False

async def connect_websocket(duration_seconds=120):
    uri = "wss://stream.bybit.com/v5/public/spot"
    symbols = [s for pair in SYMBOL_GROUPS for s in pair]
    subscribe_message = {
        "op": "subscribe",
        "args": [f"publicTrade.{symbol}" for symbol in symbols]
    }

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(subscribe_message))
        print("[WS] Подключение и подписка завершены")

        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=10)
                event = json.loads(message)
                signal = process_event(event)
                if signal:
                    await execute_trade(signal)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                await send_telegram_message(f"❗ WS ошибка: {e}")
                break

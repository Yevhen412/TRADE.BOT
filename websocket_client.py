import asyncio
import json
import time
import requests
import hmac
import hashlib
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://api.bybit.com"

# Параметры торговли
ORDER_QUANTITY = 200  # USDT
TAKE_PROFIT_PERCENT = 0.0045  # 0.45%
STOP_LOSS_PERCENT = 0.002     # 0.2%
COMMISSION = 0.0028           # 0.28%
TRADE_COOLDOWN = 5            # секунд между сделками

SYMBOL_GROUPS = [
    ("BTCUSDT", "ETHUSDT"),
    ("SOLUSDT", "AVAXUSDT"),
    ("XRPUSDT", "ADAUSDT")
]

last_prices = {}
in_trade = False
last_trade_time = 0

def get_headers(params, recv_window=5000):
    params["api_key"] = API_KEY
    params["recv_window"] = recv_window
    params["timestamp"] = int(time.time() * 1000)
    query_string = urlencode(sorted(params.items()))
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(query_string, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    params["sign"] = signature
    return params

def get_current_price(symbol: str):
    url = f"{BASE_URL}/v5/market/tickers"
    response = requests.get(url, params={"category": "spot", "symbol": symbol})
    try:
        data = response.json()
        return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None

def place_spot_order(symbol, side, usdt_amount):
    url = f"{BASE_URL}/v5/order/create"
    params = {
        "category": "spot",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": None,
        "orderLinkId": f"live_{int(time.time())}"
    }

    current_price = get_current_price(symbol)
    if not current_price:
        return {"success": False, "error": "Не удалось получить цену"}

    # Рассчитываем кол-во монет
    qty = round(usdt_amount / current_price, 6)
    params["qty"] = str(qty)

    signed = get_headers(params)
    response = requests.post(url, params=signed)
    try:
        res = response.json()
        if res.get("retCode") == 0:
            return {"success": True, "order_id": res["result"]["orderId"]}
        else:
            return {"success": False, "error": res.get("retMsg")}
    except:
        return {"success": False, "error": "Ошибка ответа от API"}

def process_event(event):
    topic = event.get("topic", "")
    data = event.get("data", [])
    if not topic or not isinstance(data, list) or not data:
        return None

    symbol = topic.split(".")[1]
    price = float(data[0]["p"])
    timestamp = time.time()
    last_prices[symbol] = (price, timestamp)
    print(f"[TICK] {symbol}: {price}")
    return check_correlation()

def check_correlation():
    global in_trade, last_trade_time
    now = time.time()
    if in_trade or now - last_trade_time < TRADE_COOLDOWN:
        return None

    for base, follower in SYMBOL_GROUPS:
        base_data = last_prices.get(base)
        follower_data = last_prices.get(follower)
        if not base_data or not follower_data:
            continue

        base_price, base_time = base_data
        follower_price, follower_time = follower_data

        if abs(now - base_time) > 1.5 or abs(now - follower_time) > 1.5:
            continue

        diff = abs(base_price - follower_price) / base_price
        if diff >= 0.003:  # 0.3%
            in_trade = True
            last_trade_time = now
            return {
                "symbol": follower,
                "entry_price": follower_price,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            }

    return None

async def execute_trade(signal, send_telegram_message):
    global in_trade
    symbol = signal["symbol"]
    entry = signal["entry_price"]
    take_profit = entry * (1 + TAKE_PROFIT_PERCENT)
    stop_loss = entry * (1 - STOP_LOSS_PERCENT)

    try:
        order_result = place_spot_order(symbol, "Buy", ORDER_QUANTITY)
        if not order_result["success"]:
            await send_telegram_message(f"❌ Не удалось купить {symbol}: {order_result['error']}")
            in_trade = False
            return

        await send_telegram_message(
            f"🟢 Покупка {symbol} по {entry:.4f} (TP: {take_profit:.4f}, SL: {stop_loss:.4f})"
        )

        while True:
            current_price = get_current_price(symbol)
            if current_price is None:
                await asyncio.sleep(1)
                continue

            if current_price >= take_profit:
                pnl = (take_profit - entry) * (ORDER_QUANTITY / entry)
                net = pnl - (ORDER_QUANTITY * COMMISSION)
                await send_telegram_message(
                    f"✅ TP {symbol} — {current_price:.4f}\nЧистая прибыль: {net:.4f} USDT"
                )
                break
            elif current_price <= stop_loss:
                pnl = (stop_loss - entry) * (ORDER_QUANTITY / entry)
                net = pnl - (ORDER_QUANTITY * COMMISSION)
                await send_telegram_message(
                    f"❌ SL {symbol} — {current_price:.4f}\nУбыток: {net:.4f} USDT"
                )
                break

            await asyncio.sleep(1)

    except Exception as e:
        await send_telegram_message(f"❗ Ошибка во время сделки {symbol}: {e}")

    finally:
        in_trade = False

async def run_trading_session(send_telegram_message, duration_seconds=120):
    import websockets

    uri = "wss://stream.bybit.com/v5/public/spot"
    symbols = [s for pair in SYMBOL_GROUPS for s in pair]
    subscribe_msg = {
        "op": "subscribe",
        "args": [f"publicTrade.{symbol}" for symbol in symbols]
    }

    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps(subscribe_msg))
            await send_telegram_message("📡 Подключено к WebSocket и подписано на пары")
            start = time.time()

            while time.time() - start < duration_seconds:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10)
                    event = json.loads(msg)
                    signal = process_event(event)
                    if signal:
                        await execute_trade(signal, send_telegram_message)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    await send_telegram_message(f"❗ Ошибка WebSocket: {e}")
                    break
    except Exception as e:
        await send_telegram_message(f"🚨 Ошибка подключения: {e}")

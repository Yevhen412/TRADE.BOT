import asyncio
import json
import time

from by_client import place_spot_order, get_current_price
from telegram_notifier import send_telegram_message

ORDER_QUANTITY = 200  # USDT
TAKE_PROFIT_PERCENT = 0.0045  # 0.45%
STOP_LOSS_PERCENT = 0.002     # 0.2%
COMMISSION = 0.0028           # 0.28%
TRADE_COOLDOWN = 5            # интервал между сделками (секунды)

SYMBOL_GROUPS = [
    ("BTCUSDT", "ETHUSDT"),
    ("SOLUSDT", "AVAXUSDT"),
    ("XRPUSDT", "ADAUSDT")
]

last_prices = {}
in_trade = False
last_trade_time = 0

__all__ = ["connect_websocket"]


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
            print(f"[SIGNAL] Correlation found: {follower}")
            in_trade = True
            last_trade_time = now
            return {
                "symbol": follower,
                "entry_price": follower_price,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            }

    return None


async def connect_websocket(duration_seconds=120):
    import websockets

    uri = "wss://stream.bybit.com/v5/public/spot"
    async with websockets.connect(uri) as ws:
        symbols = [s for pair in SYMBOL_GROUPS for s in pair]
        subscribe_message = {
            "op": "subscribe",
            "args": [f"publicTrade.{symbol}" for symbol in symbols]
        }
        await ws.send(json.dumps(subscribe_message))
        print("[WS] Подключение и подписка на пары завершены")

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
                print("[WS ERROR]", e)
                await send_telegram_message(f"❗ Ошибка WebSocket: {e}")
                break


async def execute_trade(signal):
    global in_trade
    symbol = signal["symbol"]
    entry = signal["entry_price"]
    take_profit = entry * (1 + TAKE_PROFIT_PERCENT)
    stop_loss = entry * (1 - STOP_LOSS_PERCENT)

    try:
        order_result = place_spot_order(symbol, "Buy", ORDER_QUANTITY)
        if not order_result["success"]:
            await send_telegram_message(f"❌ Ошибка покупки {symbol}: {order_result['error']}")
            in_trade = False
            return

        await send_telegram_message(f"🟢 Покупка {symbol} по {entry:.4f} (TP: {take_profit:.4f}, SL: {stop_loss:.4f})")

        while True:
            current_price = get_current_price(symbol)
            if current_price is None:
                await asyncio.sleep(1)
                continue

            if current_price >= take_profit:
                pnl = (take_profit - entry) * (ORDER_QUANTITY / entry)
                net = pnl - (ORDER_QUANTITY * COMMISSION)
                await send_telegram_message(
                    f"✅ TP достигнут {symbol} — {current_price:.4f}\nЧистая прибыль: {net:.4f} USDT")
                break

            elif current_price <= stop_loss:
                pnl = (stop_loss - entry) * (ORDER_QUANTITY / entry)
                net = pnl - (ORDER_QUANTITY * COMMISSION)
                await send_telegram_message(
                    f"❌ SL сработал {symbol} — {current_price:.4f}\nУбыток: {net:.4f} USDT")
                break

            await asyncio.sleep(1)

    except Exception as e:
        await send_telegram_message(f"❗ Ошибка сделки {symbol}: {e}")

    finally:
        in_trade = False

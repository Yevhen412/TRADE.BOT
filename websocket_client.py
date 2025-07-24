import asyncio
import json
import time
import aiohttp
import signal
from telegram_notifier import send_telegram_message
from by_client import place_spot_order, get_current_price

ORDER_QUANTITY = 200
COMMISSION = 0.0028
TRADE_COOLDOWN = 5

SYMBOL_GROUPS = [
    ("BTCUSDT", "ETHUSDT"),
    ("SOLUSDT", "AVAXUSDT"),
    ("XRPUSDT", "ADAUSDT")
]

last_prices = {}
in_trade = False
last_trade_time = 0
session_active = True

trade_state = {
    "symbol": None,
    "entry": None,
    "exit": None
}

def handle_sigterm(*_):
    global session_active
    print("🛑 SIGTERM получен. Завершаем сессию...")
    session_active = False

signal.signal(signal.SIGTERM, handle_sigterm)

async def connect_websocket(duration_seconds=120):
    global session_active, last_prices, in_trade, last_trade_time, trade_state

    session_active = True
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = [s for group in SYMBOL_GROUPS for s in group]
    end_time = time.time() + duration_seconds

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            for pair in pairs:
                await ws.send_json({
                    "op": "subscribe",
                    "args": [f"tickers.{pair}"]
                })

            while session_active:
                if time.time() > end_time:
                    session_active = False
                    break

                msg = await ws.receive(timeout=1)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await process_event(data)
                    except Exception as e:
                        print(f"[ERROR] {e}")

                await asyncio.sleep(0.01)

    await send_telegram_message("✅ WebSocket-сессия завершена.")
    await complete_trade()  # если есть незавершённая сделка — закрыть

async def process_event(event):
    global last_prices, in_trade, last_trade_time, trade_state

    if event.get("topic", "").startswith("tickers."):
        symbol = event["topic"].split(".")[1]
        price = float(event["data"]["lastPrice"])
        last_prices[symbol] = price

        for sym1, sym2 in SYMBOL_GROUPS:
            if sym1 in last_prices and sym2 in last_prices:
                p1 = last_prices[sym1]
                p2 = last_prices[sym2]
                diff = abs(p1 / p2 - 1)

                if diff > 0.003 and not in_trade and time.time() - last_trade_time > TRADE_COOLDOWN:
                    leading = sym1 if p1 / p2 > 1 else sym2
                    await send_telegram_message(f"[SIGNAL] Correlation: {leading}")

                    result = await place_spot_order(leading, ORDER_QUANTITY, "Buy")
                    if result:
                        trade_state["symbol"] = leading
                        trade_state["entry"] = result["price"]
                        in_trade = True
                        last_trade_time = time.time()
                        await send_telegram_message(f"✅ Buy {leading} @ {result['price']:.4f}")
                        asyncio.create_task(schedule_sell())  # планируем продажу

async def schedule_sell():
    await asyncio.sleep(120)
    await complete_trade()

async def complete_trade():
    global in_trade, trade_state

    if not in_trade or not trade_state["symbol"]:
        return

    result = await place_spot_order(trade_state["symbol"], ORDER_QUANTITY, "Sell")
    if result:
        trade_state["exit"] = result["price"]
        entry = trade_state["entry"]
        exit_price = trade_state["exit"]
        gross = (exit_price - entry) * ORDER_QUANTITY
        net = gross - (ORDER_QUANTITY * entry * COMMISSION) - (ORDER_QUANTITY * exit_price * COMMISSION)

        status = "✅ Profit" if net >= 0 else "❌ Loss"

        await send_telegram_message(
            f"📊 <b>{trade_state['symbol']}</b>\n"
            f"Entry: {entry:.4f}\n"
            f"Exit: {exit_price:.4f}\n"
            f"Net: {net:.4f} USDT\n"
            f"Result: {status}"
        )

    in_trade = False
    trade_state["symbol"] = None
    trade_state["entry"] = None
    trade_state["exit"] = None

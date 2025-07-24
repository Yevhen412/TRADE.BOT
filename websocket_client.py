import asyncio
import json
import time
import aiohttp
import signal
from datetime import datetime
from telegram_notifier import send_telegram_message
from by_client import place_spot_order, get_current_price

ORDER_QUANTITY = 200  # USDT
TAKE_PROFIT_PERCENT = 0.0045
STOP_LOSS_PERCENT = 0.002
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
trade_log = []


def handle_sigterm(*_):
    global session_active
    print("🛑 SIGTERM получен. Завершаем сессию...")
    session_active = False


signal.signal(signal.SIGTERM, handle_sigterm)


async def connect_websocket(duration_seconds=120):
    global session_active, last_prices, in_trade, last_trade_time

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

            while time.time() < end_time and session_active:
                msg = await ws.receive(timeout=5)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await process_event(data)
                    except Exception as e:
                        print(f"[ERROR] {e}")
                await asyncio.sleep(0.01)

            await send_telegram_message("✅ WebSocket сессия завершена.")
            await send_summary()


async def process_event(event):
    global last_prices, in_trade, last_trade_time

    if event.get("topic", "").startswith("tickers."):
        symbol = event["topic"].split(".")[1]
        price = float(event["data"]["lastPrice"])
        last_prices[symbol] = price

        for sym1, sym2 in SYMBOL_GROUPS:
            if sym1 in last_prices and sym2 in last_prices:
                p1 = last_prices[sym1]
                p2 = last_prices[sym2]
                diff_percent = abs(p1 / p2 - 1)

                if diff_percent > 0.003 and not in_trade and time.time() - last_trade_time > TRADE_COOLDOWN:
                    leading = sym1 if p1 / p2 > 1 else sym2
                    entry_price = await get_current_price(leading)
                    if not entry_price:
                        return

                    take_profit = entry_price * (1 + TAKE_PROFIT_PERCENT)
                    stop_loss = entry_price * (1 - STOP_LOSS_PERCENT)
                    net_profit = (ORDER_QUANTITY * TAKE_PROFIT_PERCENT) - (ORDER_QUANTITY * COMMISSION)

                    if net_profit >= 0.03:
                        success = await place_spot_order(leading, ORDER_QUANTITY)
                        if success:
                            in_trade = True
                            last_trade_time = time.time()
                            await send_telegram_message(f"[SIGNAL] Покупка {leading} по цене {entry_price:.4f}")
                            await monitor_trade(leading, entry_price)
                    else:
                        await send_telegram_message(f"❌ Сигнал отклонён: net profit {net_profit:.4f}")


async def monitor_trade(symbol, entry_price):
    global in_trade, trade_log

    take_profit = entry_price * (1 + TAKE_PROFIT_PERCENT)
    stop_loss = entry_price * (1 - STOP_LOSS_PERCENT)
    side = "LONG"
    time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    while True:
        await asyncio.sleep(1)
        current_price = await get_current_price(symbol)
        if not current_price:
            continue

        if current_price >= take_profit or current_price <= stop_loss:
            exit_price = current_price
            gross = abs(exit_price - entry_price)
            fee = round(gross * COMMISSION, 4)
            net = round(gross - fee, 4)
            result = "PROFIT" if net > 0 else "LOSS"

            trade_log.append({
                "symbol": symbol,
                "entry": entry_price,
                "exit": exit_price,
                "net": net,
                "side": side,
                "time": time_str,
                "result": result
            })

            in_trade = False

            if net > 0:
                await send_telegram_message(
                    f"📊 <b>Trade Executed</b>\n"
                    f"Pair: {symbol}\n"
                    f"Time: {time_str}\n"
                    f"Side: {side}\n"
                    f"Entry: {entry_price:.4f}\n"
                    f"Exit: {exit_price:.4f}\n"
                    f"Net: {net:.4f} USDT\n"
                    f"Result: {result}"
                )
            else:
                print("🧯 Сделка неуспешна, Telegram не уведомляется.")
            break


async def send_summary():
    if not trade_log:
        await send_telegram_message("📉 Нет совершённых сделок за сессию.")
        return

    total = sum(t["net"] for t in trade_log)
    summary = "📋 <b>Session Summary</b>\n\n"
    for t in trade_log:
        summary += (
            f"📌 {t['symbol']}: {t['result']} | Net: {t['net']:.4f} USDT\n"
        )
    summary += f"\n💰 <b>Total PnL: {total:.4f} USDT</b>"
    await send_telegram_message(summary)
    trade_log.clear()

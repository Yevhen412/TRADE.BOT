import asyncio
import os
import json
import time
import hmac
import hashlib
import aiohttp
import signal
from urllib.parse import urlencode

from telegram_notifier import send_telegram_message
from by_client import place_spot_order, get_current_price

__all__ = ["connect_websocket"]

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

ORDER_QUANTITY = 200  # USDT
TAKE_PROFIT_PERCENT = 0.0045  # 0.45%
STOP_LOSS_PERCENT = 0.002  # 0.2%
COMMISSION = 0.0028  # 0.28%
TRADE_COOLDOWN = 5  # интервал между сделками

SYMBOL_GROUPS = [
    ("BTCUSDT", "ETHUSDT"),
    ("SOLUSDT", "AVAXUSDT"),
    ("XRPUSDT", "ADAUSDT")
]

last_prices = {}
in_trade = False
last_trade_time = 0
session_active = True  # Флаг активности сессии

def handle_sigterm(*_):
    global session_active
    print("🛑 SIGTERM получен. Завершаем сессию...")
    session_active = False

# Привязка обработчика сигнала
signal.signal(signal.SIGTERM, handle_sigterm)

def generate_signature(params: dict) -> str:
    query_string = urlencode(params)
    return hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

async def connect_websocket(duration_seconds=120):
    global session_active, last_prices, in_trade, last_trade_time

    session_active = True
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = [symbol for group in SYMBOL_GROUPS for symbol in group]
    end_time = time.time() + duration_seconds

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            for pair in pairs:
                await ws.send_json({
                    "op": "subscribe",
                    "args": [f"tickers.{pair}"]
                })

            async for msg in ws:
                if time.time() > end_time or not session_active:
                    await send_telegram_message("✅ WebSocket сессия завершена.")
                    break

                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await process_event(data)
                    except Exception as e:
                        print(f"[ERROR] {e}")

                await asyncio.sleep(0.01)

async def process_event(event):
    global last_prices, in_trade, last_trade_time

    if event.get("topic", "").startswith("tickers."):
        symbol = event["topic"].split(".")[1]
        price = float(event["data"]["lastPrice"])
        print(f"[TICK] {symbol}: {price}")
        last_prices[symbol] = price

        for sym1, sym2 in SYMBOL_GROUPS:
            if sym1 in last_prices and sym2 in last_prices:
                p1 = last_prices[sym1]
                p2 = last_prices[sym2]
                diff_percent = abs(p1 / p2 - 1)

                if diff_percent > 0.003 and not in_trade and time.time() - last_trade_time > TRADE_COOLDOWN:
                    leading = sym1 if p1 / p2 > 1 else sym2
                    await send_telegram_message(f"[SIGNAL] Correlation found: {leading}")

                    entry_price = await get_current_price(leading)
                    if not entry_price:
                        return

                    take_profit = entry_price * (1 + TAKE_PROFIT_PERCENT)
                    stop_loss = entry_price * (1 - STOP_LOSS_PERCENT)
                    target_profit = ORDER_QUANTITY * TAKE_PROFIT_PERCENT
                    target_loss = ORDER_QUANTITY * STOP_LOSS_PERCENT
                    est_commission = ORDER_QUANTITY * COMMISSION

                    net_profit = target_profit - est_commission

                    if net_profit >= 0.03:
                        success = await place_spot_order(leading, ORDER_QUANTITY)
                        if success:
                            in_trade = True
                            last_trade_time = time.time()
                            await send_telegram_message(f"✅ Покупка {leading} по цене {entry_price:.4f}")
                    else:
                        await send_telegram_message(f"❌ Сигнал отклонён: net profit {net_profit:.4f}")

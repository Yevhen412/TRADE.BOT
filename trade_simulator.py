from datetime import datetime
import time
import os
from pybit.unified_trading import HTTP

# Инициализация реальных сессий Bybit
session_spot = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

session_futures = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    testnet=False
)

class TradeSimulator:
    def __init__(self):
        self.in_trade = False
        self.last_trade_time = 0
        self.delay_between_trades = 2  # секунды
        self.last_prices = {}
        self.trade_log = []

    def process(self, event):
        try:
            topic = event.get("topic", "")
            data = event.get("data", [])
            if not topic or not isinstance(data, list) or not data:
                return None

            symbol = topic.split(".")[1]
            price = float(data[0]["p"])
            timestamp = time.time()

            self.last_prices[symbol] = (price, timestamp)
            print(f"[DEBUG] Получен тик: {symbol} → {price}")
            return self.check_correlation()
        except Exception as e:
            print("❌ Ошибка в process:", e)
            return None

    def check_correlation(self):
        now = time.time()
        if self.in_trade or now - self.last_trade_time < self.delay_between_trades:
            return None

        groups = [
            ("BTCUSDT", "ETHUSDT"),
            ("SOLUSDT", "AVAXUSDT"),
            ("XRPUSDT", "ADAUSDT")
        ]

        for base, follower in groups:
            base_data = self.last_prices.get(base)
            follower_data = self.last_prices.get(follower)
            if not base_data or not follower_data:
                continue

            base_price, base_time = base_data
            follower_price, follower_time = follower_data

            if now - base_time > 1.5 or now - follower_time > 1.5:
                continue

            diff = abs(base_price - follower_price) / base_price
            if diff > 0.003:  # > 0.3%
                self.in_trade = True
                self.last_trade_time = now

                side = "LONG" if base_price > follower_price else "SHORT"
                entry = follower_price

                signal = {
                    "symbol": follower,
                    "entry_price": round(entry, 4),
                    "side": side,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }

                print(f"[DEBUG] Сигнал создан: {signal}")
                return signal
        return None

    async def execute_trade(self, signal):
        from telegram_notifier import send_telegram_message  # импорт здесь, чтобы избежать циклов

        if not signal:
            return None

        symbol = signal["symbol"]
        side = signal["side"]
        entry = signal["entry_price"]
        time_str = signal["timestamp"]

        qty = 10  # Тестовая фиксированная величина (позже можно сделать динамической)

        try:
            if side == "LONG":
                order = session_spot.place_order(
                    category="spot",
                    symbol=symbol,
                    side="Buy",
                    order_type="Market",
                    qty=qty
                )
            else:
                order = session_futures.place_order(
                    category="linear",
                    symbol=symbol,
                    side="Sell",
                    order_type="Market",
                    qty=qty,
                    reduce_only=False
                )

            print("✅ Сделка прошла:", order)

            self.in_trade = False

            return (
                f"📈 <b>Real Trade Executed</b>\n"
                f"Pair: {symbol}\n"
                f"Time: {time_str}\n"
                f"Side: {side}\n"
                f"Qty: {qty}\n"
                f"Entry: {entry}"
            )

        except Exception as e:
            self.in_trade = False
            print("❌ Ошибка при торговле:", e)
            return f"❌ Ошибка при торговле по {symbol}: {e}"

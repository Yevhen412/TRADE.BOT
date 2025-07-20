from datetime import datetime
import time
import os
from pybit.unified_trading import HTTP

class TradeSimulator:
    def __init__(self):
        self.in_trade = False
        self.last_trade_time = 0
        self.delay_between_trades = 5  # ⏱️ 5 секунд между сделками
        self.last_prices = {}
        self.trade_log = []

        self.session = HTTP(
            api_key=os.getenv("API_KEY"),
            api_secret=os.getenv("API_SECRET"),
        )

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
            if diff > 0.003:
                self.in_trade = True
                

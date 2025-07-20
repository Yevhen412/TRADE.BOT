from datetime import datetime
import time

class TradeSimulator:
    def __init__(self):
        self.in_trade = False
        self.last_trade_time = 0
        self.delay_between_trades = 5  # сек между сделками
        self.last_prices = {}
        self.trade_log = []

        # Комиссии
        self.spot_fee = 0.0018  # 0.18%
        self.futures_fee = 0.0010  # 0.10%

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
                self.last_trade_time = now

                side = "LONG" if base_price > follower_price else "SHORT"
                entry = follower_price

                # Расчёт комиссии
                fee_total = self.spot_fee + self.futures_fee
                target_profit = entry * fee_total + 0.01  # чистая прибыль минимум $0.01

                exit_price = entry + target_profit if side == "LONG" else entry - target_profit

                signal = {
                    "symbol": follower,
                    "entry_price": round(entry, 4),
                    "exit_price": round(exit_price, 4),
                    "side": side,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }

                print(f"[DEBUG] Сигнал создан: {signal}")
                return signal
        return None

    def simulate_trade(self, signal):
        if not signal:
            return None

        entry = signal["entry_price"]
        exit = signal["exit_price"]
        side = signal["side"]
        symbol = signal["symbol"]
        time_str = signal["timestamp"]

        gross = abs(exit - entry)
        fee = round(entry * (self.spot_fee + self.futures_fee), 4)
        net = round(gross - fee, 4)
        result = "PROFIT" if net > 0 else "LOSS"

        self.in_trade = False
        self.trade_log.append((symbol, time_str, side, entry, exit, net))

        if net <= 0:
            print("🔕 Сделка неуспешна, Telegram не уведомляется.")
            return None

        return (
            f"📊 <b>Trade Executed</b>\n"
            f"Pair: {symbol}\n"
            f"Time: {time_str}\n"
            f"Side: {side} (Spot long / Futures short)\n"
            f"Entry: {entry}\n"
            f"Exit: {exit}\n"
            f"Net: {net:.4f} USDT\n"
            f"Result: {result}"
        )

    def generate_pnl_report(self):
        if not self.trade_log:
            return "📉 Нет завершённых сделок за сессию."

        total_net = sum([log[5] for log in self.trade_log])
        count = len(self.trade_log)
        report = f"📈 <b>Session PnL Report</b>\n"
        report += f"Trades: {count}\n"
        report += f"Net Profit: {round(total_net, 4)} USDT"

        self.trade_log.clear()
        return report

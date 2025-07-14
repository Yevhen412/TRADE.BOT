
from datetime import datetime

class TradeSimulator:
    def __init__(self):
        self.in_trade = False

    def process(self, event):
        return self.generate_signal(event)

    def generate_signal(self, event):
        try:
            data = event.get("data", [])
            if not isinstance(data, list) or not data:
                return None
            trade = data[0]
            price = float(trade.get("p"))
            return {
                "entry_price": price,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "side": "SHORT",
                "exit_price": round(price * 0.99, 4),
            }
        except Exception as e:
            print(f"Ошибка в generate_signal: {e}")
            return None

    def simulate_trade(self, signal):
        if self.in_trade:
            return None
        self.in_trade = True

        entry = signal["entry_price"]
        exit = signal["exit_price"]
        side = signal["side"]
        time = signal["timestamp"]
        gross = round(abs(entry - exit), 4)
        fee = round(gross * 0.285, 4)
        net = round(gross - fee, 4)
        result = "PROFIT" if net > 0 else "LOSS"

        self.in_trade = False

        return (
            f"<b>Trade Report</b>\n"
            f"Time: {time}\n"
            f"Side: {side}\n"
            f"Entry: {entry}\n"
            f"Exit: {exit}\n"
            f"Gross: {gross} USDT\n"
            f"Fee: {fee} USDT\n"
            f"Net: {net} USDT\n"
            f"Result: {result}"
        )

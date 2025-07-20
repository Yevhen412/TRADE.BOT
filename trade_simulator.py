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

        # Добавлено для финального отчета
        self.total_profit = 0
        self.total_loss = 0
        self.win_count = 0
        self.loss_count = 0

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
                self.last_trade_time = now
                return {"pair": follower, "side": "buy", "price": follower_price}

        return None

    async def execute_trade(self, signal):
        """
        Заглушка исполнения сделки. Здесь можно подключить реальный API или оставить как симуляцию.
        """
        price = signal["price"]
        side = signal["side"]
        pair = signal["pair"]

        profit = round((price * 0.002), 4)  # симулируем прибыль 0.2%
        is_win = True  # можно сделать рандом

        # Логика фиксации результата
        if is_win:
            self.total_profit += profit
            self.win_count += 1
        else:
            self.total_loss += profit
            self.loss_count += 1

        self.in_trade = False

        now = datetime.now().strftime("%H:%M:%S")
        return f"🟢 Сделка: {pair} {side.upper()} по {price}\n📈 {'+Profit' if is_win else '-Loss'}: {profit}\n🕒 {now}"

    def get_session_pnl_report(self):
        total_profit = round(self.total_profit, 4)
        total_loss = round(self.total_loss, 4)
        net_result = round(total_profit - total_loss, 4)
        win_count = self.win_count
        loss_count = self.loss_count

        return (
            f"📊 *Результаты сессии:*\n"
            f"➕ Прибыльных сделок: {win_count}\n"
            f"➖ Убыточных сделок: {loss_count}\n"
            f"💰 Итоговая прибыль: {total_profit}\n"
            f"💸 Итоговый убыток: {total_loss}\n"
            f"📈 Чистый результат: {net_result}"
    )

# trade_simulator.py

class TradeSimulator:
    def __init__(self):
        self.session_trades = []

    def process(self, event):
        # Заглушка, пока не используется
        return None

    def simulate_trade(self, signal):
        # Фиктивная сделка: вход 100 USDT по 1.0000, выход по 1.0100
        entry_price = 1.0000
        exit_price = 1.0100
        amount_usdt = 100
        volume = amount_usdt / entry_price  # сколько куплено
        pnl = (exit_price - entry_price) * volume

        trade = {
            "entry": entry_price,
            "exit": exit_price,
            "amount": amount_usdt,
            "pnl": pnl
        }
        self.session_trades.append(trade)
        return trade

    def get_session_pnl_report(self):
        if not self.session_trades:
            return "Нет сделок в этой сессии."

        total_pnl = sum(t["pnl"] for t in self.session_trades)
        trade_count = len(self.session_trades)

        report = f"Сделок: {trade_count}\nОбщий PnL: {total_pnl:.2f} USDT"
        return report

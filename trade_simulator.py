# trade_simulator.py
# Заглушка: симулятор отключён, используем живую торговлю

import asyncio 

class TradeSimulator:
    def process(self, event):
        return None

    def simulate_trade(self, signal):
        return None

    def get_session_pnl_report(self):
        return "Симуляция отключена. Используется живая торговля."

async def run_trading_session():
    await asyncio.sleep(2 * 60)  # Ждём 2 минуты
    return "Сессия завершена. Торговля отключена. Это заглушка."

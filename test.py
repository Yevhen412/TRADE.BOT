import asyncio
import os
from bybit_websocket import BybitWebSocket
from trade_simulator import TradeSimulator
from telegram_bot import notify_telegram, bot_should_run

simulator = TradeSimulator()

async def send_hourly_report():
    while True:
        await asyncio.sleep(3600)
        report = simulator.generate_hourly_report()
        if report:
            await notify_telegram(report)

async def main():
    await notify_telegram("🟢 Бот запущен и ожидает сигналы...")
    ws = BybitWebSocket()
    asyncio.create_task(send_hourly_report())

    async for event in ws.listen():
        if not bot_should_run():
            continue

        signal = simulator.process(event)
        if signal:
            result_msg = simulator.simulate_trade(signal)
            if result_msg:
                await notify_telegram(result_msg)

if __name__ == "__main__":
    asyncio.run(main())

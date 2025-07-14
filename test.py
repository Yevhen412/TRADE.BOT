
import asyncio
import os
import aiohttp
from trade_simulator import TradeSimulator

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot_active = True

simulator = TradeSimulator()

async def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Переменные окружения не заданы!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)

async def handle_trade_event(event):
    global bot_active
    if not bot_active:
        return
    signal = simulator.process(event)
    if signal:
        result_msg = simulator.simulate_trade(signal)
        if result_msg:
            await send_telegram_message(result_msg)

async def telegram_control_loop():
    global bot_active
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    offset = None
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"timeout": 10}
                if offset:
                    params["offset"] = offset
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        message = update.get("message", {}).get("text", "")
                        if message == "/stop":
                            bot_active = False
                            await send_telegram_message("⏹ Бот остановлен.")
                        elif message == "/start":
                            bot_active = True
                            await send_telegram_message("▶️ Бот запущен.")
        except Exception as e:
            print(f"Ошибка контроля Telegram: {e}")
        await asyncio.sleep(3)

async def main():
    await send_telegram_message("✅ Бот запущен.")
    await asyncio.gather(
        telegram_control_loop(),
    )

if __name__ == "__main__":
    asyncio.run(main())

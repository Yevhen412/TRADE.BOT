import asyncio
import os
from dotenv import load_dotenv
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

simulator = TradeSimulator()
is_session_running = False

async def handle_start():
    global is_session_running
    is_session_running = True

    await send_telegram_message("✅ Сессия запущена на 2 минуты…")

    # Фиктивная сделка
    trade = simulator.simulate_trade(None)
    await send_telegram_message(
        f"🟢 Фиктивная сделка: Вход {trade['entry']}, Выход {trade['exit']}, Прибыль: {trade['pnl']:.2f} USDT"
    )

    await asyncio.sleep(120)

    # Отчёт по сессии
    report = simulator.get_session_pnl_report()
    await send_telegram_message(f"📊 Итог сессии:\n{report}")
    is_session_running = False

async def polling_loop():
    import httpx

    API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
    offset = None

    while True:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{API_URL}/getUpdates", params={"offset": offset})
                updates = resp.json().get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    text = msg.get("text", "")

                    if chat_id == CHAT_ID and text == "/start":
                        if is_session_running:
                            await send_telegram_message("⏳ Уже идёт сессия…")
                        else:
                            asyncio.create_task(handle_start())

        except Exception as e:
            print("❌ Ошибка polling:", e)

        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(polling_loop())

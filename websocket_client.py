import asyncio
import aiohttp
import json
import time
from trade_simulator import TradeSimulator
from telegram_notifier import send_telegram_message

simulator = TradeSimulator()
last_msg_time = time.time()
INACTIVITY_TIMEOUT = 600  # 10 минут

async def run_session():
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "ADAUSDT"]
    topics = [f"publicTrade.{pair}" for pair in pairs]

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            print("🌐 WebSocket подключен")
            await ws.send_json({"op": "subscribe", "args": topics})
            asyncio.create_task(watchdog(ws))

            end_time = time.time() + 120  # 2 минуты
            async for msg in ws:
                if time.time() > end_time:
                    await send_telegram_message("⏹️ 2 минуты прошли. Сессия завершена.")
                    await ws.close()
                    break

                if msg.type == aiohttp.WSMsgType.TEXT:
                    global last_msg_time
                    last_msg_time = time.time()
                    try:
                        event = json.loads(msg.data)
                        signal = simulator.process(event)
                        if signal:
                            message = simulator.simulate_trade(signal)
                            if message:
                                await send_telegram_message(message)
                    except Exception as e:
                        print("❌ Ошибка:", e)

async def watchdog(ws):
    while True:
        await asyncio.sleep(10)
        if time.time() - last_msg_time > INACTIVITY_TIMEOUT:
            await send_telegram_message("⚠️ WebSocket завис. Закрываю соединение.")
            await ws.close()
            break

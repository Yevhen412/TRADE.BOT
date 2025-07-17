import asyncio
import aiohttp
import json
import time
from trade_simulator import TradeSimulator
from telegram_notifier import notify_telegram

simulator = TradeSimulator()
last_msg_time = time.time()
INACTIVITY_TIMEOUT = 600  # 10 минут

async def connect_websocket():
    print("🚀 connect_websocket() вызвана")  # <-- Добавлено для логов
    global last_msg_time
    url = "wss://stream.bybit.com/v5/public/spot"
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "ADAUSDT"]
    topics = [f"publicTrade.{pair}" for pair in pairs]

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            print("🌐 Подключено к WebSocket")

            await ws.send_json({
                "op": "subscribe",
                "args": topics
            })

            # Стартуем watchdog
            asyncio.create_task(watchdog(ws))

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    last_msg_time = time.time()
                    try:
                        event = json.loads(msg.data)
                        signal = simulator.process(event)
                        if signal:
                            message = simulator.simulate_trade(signal)
                            if message:
                                await notify_telegram(message)
                    except Exception as e:
                        print("❌ Ошибка обработки сообщения:", e)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("❌ Ошибка WebSocket:", msg)
                    break

async def watchdog(ws):
    while True:
        await asyncio.sleep(10)
        if time.time() - last_msg_time > INACTIVITY_TIMEOUT:
            print("⚠️ Нет сообщений от WebSocket, перезапускаем...")
            await notify_telegram("⚠️ WebSocket завис — перезапускаю соединение...")
            await ws.close()
            return

# ⬇️ Добавляем алиас для server.py
connect = connect_websocket

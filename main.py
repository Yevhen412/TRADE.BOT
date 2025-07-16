import asyncio
import json
import os
import websockets
import aiohttp

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

async def send_telegram_heartbeat():
    while True:
        if not BOT_TOKEN or not CHAT_ID:
            print("❌ BOT_TOKEN или CHAT_ID не заданы!")
        else:
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": CHAT_ID,
                    "text": "Я жив 🟢",
                    "parse_mode": "HTML"
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=payload) as response:
                        text = await response.text()
                        print("💬 Telegram ответ:", text)
            except Exception as e:
                print("❌ Ошибка отправки Telegram:", e)
        await asyncio.sleep(10)

async def listen_websocket():
    uri = "wss://stream.bybit.com/v5/public/spot"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "op": "subscribe",
            "args": [
                "publicTrade.BTCUSDT"
            ]
        }))
        print("📡 Подписка на WebSocket завершена")

        while True:
            try:
                response = await websocket.recv()
                message = json.loads(response)
                if "topic" in message:
                    print("📈 Пришёл тик:", message["data"][0]["p"])
            except Exception as e:
                print("❌ Ошибка в WebSocket:", e)
                await asyncio.sleep(5)

async def main():
    print("🚀 main.py запущен")
    print("🌐 ENV:", {k: v for k, v in os.environ.items() if "TOKEN" in k or "CHAT" in k})
    await asyncio.gather(
        listen_websocket(),
        send_telegram_heartbeat()
    )

if __name__ == "__main__":
    asyncio.run(main())

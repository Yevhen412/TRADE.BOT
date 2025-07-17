import asyncio
import os
from aiohttp import web
from datetime import datetime, timedelta
from main import connect  # Импортируем WebSocket-цикл
from telegram_notifier import send_telegram_message

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
SECRET_TOKEN = os.getenv("TELEGRAM_SECRET", "my_secret").strip()  # секрет можно задать для безопасности

running = False
last_start_time = datetime.min

routes = web.RouteTableDef()

@routes.post(f"/{SECRET_TOKEN}/start")
async def handle_start(request):
    global running, last_start_time

    now = datetime.utcnow()

    if running:
        return web.Response(text="⏳ Бот уже работает. Подожди окончания цикла.")

    if now - last_start_time < timedelta(minutes=3):
        remaining = 180 - int((now - last_start_time).total_seconds())
        return web.Response(text=f"⛔ Повторный запуск возможен через {remaining} сек.")

    running = True
    last_start_time = now

    asyncio.create_task(run_with_timeout())

    await send_telegram_message("▶️ Стратегия запущена вручную. Работа в течение 2 минут.")
    return web.Response(text="✅ Запущено на 2 минуты.")

async def run_with_timeout():
    global running
    try:
        task = asyncio.create_task(connect())
        await asyncio.sleep(120)
        task.cancel()
        await send_telegram_message("⏹️ Время истекло. Бот приостановлен. Повторный запуск через 3 минуты.")
    except Exception as e:
        print("❌ Ошибка run_with_timeout:", e)
    finally:
        running = False

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=8080)

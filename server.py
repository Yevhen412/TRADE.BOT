from aiohttp import web
import asyncio
import os
from main import main  # Импортируем функцию, запускающую бота

RUNNING = False
LAST_RUN = 0

async def handle_start(request):
    global RUNNING, LAST_RUN

    now = asyncio.get_event_loop().time()
    if RUNNING or (now - LAST_RUN) < 180:  # не раньше чем через 3 минуты
        return web.Response(text="⏳ Уже запущено или слишком рано.")

    RUNNING = True
    LAST_RUN = now
    asyncio.create_task(run_bot())
    return web.Response(text="🚀 Бот запущен на 2 минуты.")

async def run_bot():
    global RUNNING
    try:
        await main()
    finally:
        RUNNING = False

app = web.Application()
app.router.add_get('/start', handle_start)

if __name__ == '__main__':
    web.run_app(app, port=int(os.environ.get("PORT", 8080)))

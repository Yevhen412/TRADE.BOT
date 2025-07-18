from fastapi import FastAPI
import asyncio
from websocket_client import run_session
import uvicorn

app = FastAPI()

is_running = False
last_run_time = 0


@app.get("/")
def root():
    return {"message": "Bot is online. Go to /resume to start."}


@app.get("/resume")
async def resume():
    global is_running, last_run_time

    if is_running:
        return {"message": "Already running"}

    # проверка паузы в 3 минуты
    now = asyncio.get_event_loop().time()
    if now - last_run_time < 180:
        remaining = int(180 - (now - last_run_time))
        return {"message": f"Подожди {remaining} секунд перед следующим запуском"}

    is_running = True
    last_run_time = now

    async def background():
        global is_running
        try:
            await run_session()
        except Exception as e:
            print(f"Ошибка в run_session: {e}")
        await asyncio.sleep(120)  # 2 минуты работы
        is_running = False
        print("Сессия завершена, бот остановлен.")

    asyncio.create_task(background())
    return {"message": "Сессия запущена на 2 минуты"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)

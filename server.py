from fastapi import FastAPI
import asyncio
from websocket_client import run_session

app = FastAPI()

# Флаг, чтобы не запускать новую сессию, пока старая не завершилась
is_running = False

@app.get("/")
def read_root():
    return {"status": "Bot is up. Use /resume to start session."}

@app.get("/resume")
async def resume_session():
    global is_running

    if is_running:
        return {"status": "Session already running"}

    is_running = True

    async def session_wrapper():
        global is_running
        try:
            await run_session()
        finally:
            is_running = False

    asyncio.create_task(session_wrapper())

    return {"status": "Session started"}

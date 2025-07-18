from fastapi import FastAPI
import asyncio
from websocket_client import run_session

app = FastAPI()

is_running = False

@app.get("/")
def home():
    return {"status": "Bot is online. Use /resume to start session"}

@app.get("/resume")
async def resume_session():
    global is_running
    if is_running:
        return {"status": "Already running"}

    is_running = True

    async def session():
        global is_running
        try:
            await run_session()
        finally:
            is_running = False

    asyncio.create_task(session())
    return {"status": "Session started"}

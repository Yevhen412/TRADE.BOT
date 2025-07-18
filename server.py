from fastapi import FastAPI
import asyncio
from websocket_client import run_session

app = FastAPI()

is_running = False

@app.get("/")
def root():
    return {"message": "Bot is online. Use /resume to start session."}

@app.get("/resume")
async def resume():
    global is_running
    if is_running:
        return {"message": "Already running."}
    
    is_running = True

    async def background():
        global is_running
        try:
            await run_session()
        finally:
            is_running = False

    asyncio.create_task(background())
    return {"message": "Session started."}

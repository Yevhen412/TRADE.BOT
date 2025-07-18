from fastapi import FastAPI
import asyncio
from websocket_client import connect_websocket

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(connect_websocket())

@app.get("/start")
async def start():
    return {"message": "Все работает"}

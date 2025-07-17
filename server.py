from websocket_client import connect_websocket as connect
import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/start")
async def start():
    asyncio.create_task(connect())
    return JSONResponse(content={"message": "Процесс запущен на 2 минуты..."})

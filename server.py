from fastapi import FastAPI

app = FastAPI()

@app.get("/start")
async def start():
    return {"message": "Asyncio работает"}

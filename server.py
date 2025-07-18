import asyncio
from websocket_client import run_session

def run():
    print("🚀 Сессия запускается...")
    asyncio.run(run_session())

if __name__ == "__main__":
    run()

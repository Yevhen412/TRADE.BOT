import os
import time
import hmac
import hashlib
import aiohttp
from urllib.parse import urlencode

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"

def generate_signature(params: dict) -> str:
    query_string = urlencode(sorted(params.items()))
    return hmac.new(API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

async def get_current_price(symbol: str) -> float:
    url = f"{BASE_URL}/v5/market/tickers"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params={"category": "spot", "symbol": symbol}) as response:
                data = await response.json()
                return float(data["result"]["list"][0]["lastPrice"])
        except Exception as e:
            print(f"[ERROR] get_current_price: {e}")
            return None

async def place_spot_order(symbol: str, qty: float) -> bool:
    url = f"{BASE_URL}/v5/order/create"
    timestamp = int(time.time() * 1000)

    params = {
        "symbol": symbol,
        "side": "Buy",
        "orderType": "Market",
        "qty": qty,
        "timestamp": timestamp,
        "apiKey": API_KEY
    }

    print(f"[DEBUG] Sending order with:")
    print(f"API_KEY: {API_KEY}")
    print(f"API_SECRET: {API_SECRET}")
    print(f"params: {params}")

    sign = generate_signature(params)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    params["sign"] = sign

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=params, headers=headers) as response:
                data = await response.json()
                print(f"[ORDER RESPONSE] {data}")
                return data["retCode"] == 0
        except Exception as e:
            print(f"[ERROR] place_spot_order: {e}")
            return False

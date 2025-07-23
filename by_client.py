import time
import hmac
import hashlib
import aiohttp
import os
from urllib.parse import urlencode

BASE_URL = "https://api.bybit.com"
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def generate_signature(params: dict) -> str:
    sorted_params = dict(sorted(params.items()))
    query_string = urlencode(sorted_params)
    return hmac.new(
        API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

async def get_current_price(symbol: str) -> float:
    url = f"{BASE_URL}/v5/market/tickers"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"category": "spot", "symbol": symbol}) as resp:
                data = await resp.json()
                return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None

async def place_spot_order(symbol: str, qty: float) -> bool:
    url = f"{BASE_URL}/v5/order/create"
    timestamp = str(int(time.time() * 1000))

    params = {
        "symbol": symbol,
        "side": "Buy",
        "orderType": "Market",
        "qty": qty,
        "timestamp": timestamp,
        "apiKey": API_KEY,
    }

    sign = generate_signature(params)
    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "X-BYBIT-TIMESTAMP": timestamp,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    encoded_params = urlencode(params)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=encoded_params, headers=headers) as resp:
                data = await resp.json()
                print(f"[ORDER RESPONSE] {data}")
                return data.get("retCode") == 0
    except Exception as e:
        print(f"[ERROR] place_spot_order: {e}")
        return False

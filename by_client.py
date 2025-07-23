import time
import hmac
import hashlib
import aiohttp
import os
import json
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

async def place_spot_order(symbol: str, qty: float):
    url = f"{BASE_URL}/v5/order/create"
    timestamp = str(int(time.time() * 1000))

    body = {
        "symbol": symbol,
        "side": "Buy",
        "orderType": "Market",
        "qty": qty
    }

    recv_window = "5000"
    sign_payload = f"{timestamp}{API_KEY}{recv_window}{json.dumps(body, separators=(',', ':'))}"
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        sign_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as response:
                data = await response.json()
                print(f"[ORDER RESPONSE] {data}")
                return data["retCode"] == 0
    except Exception as e:
        print(f"[ERROR] place_spot_order: {e}")
        return False

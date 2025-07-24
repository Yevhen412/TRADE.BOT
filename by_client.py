import time
import hmac
import hashlib
import aiohttp
import os
import json

BASE_URL = "https://api.bybit.com"
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def sign_request(timestamp: str, recv_window: str, body: str) -> str:
    payload = f"{timestamp}{API_KEY}{recv_window}{body}"
    return hmac.new(
        API_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
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

async def place_spot_order(symbol: str, qty: float, side: str = "Buy"):
    if not symbol or not qty:
        print(f"[ERROR] Некорректные параметры: symbol={symbol}, qty={qty}")
        return None

    url = f"{BASE_URL}/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    body = {
        "category": "spot",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty)
    }

    json_body = json.dumps(body, separators=(",", ":"))
    signature = sign_request(timestamp, recv_window, json_body)

    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json_body) as response:
                data = await response.json()
                print(f"[ORDER RESPONSE] {data}")

                if data.get("retCode") == 0:
                    price = float(data["result"].get("avgPrice", 0))
                    return {
                        "symbol": symbol,
                        "side": side,
                        "price": price,
                        "qty": qty
                    }
                return None
    except Exception as e:
        print(f"[ERROR] place_spot_order: {e}")
        return None

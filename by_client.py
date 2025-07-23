import os
import time
import hmac
import hashlib
import aiohttp

BASE_URL = "https://api.bybit.com"
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def _get_signed_params(params: dict) -> dict:
    params["apiKey"] = API_KEY
    params["timestamp"] = int(time.time() * 1000)
    sorted_params = dict(sorted(params.items()))
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    sorted_params["sign"] = signature
    return sorted_params

async def get_current_price(symbol: str) -> float:
    url = f"{BASE_URL}/v5/market/tickers"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"category": "spot", "symbol": symbol}) as response:
                data = await response.json()
                return float(data["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"[ERROR] get_current_price: {e}")
        return None

async def place_spot_order(symbol: str, quantity: float) -> bool:
    url = f"{BASE_URL}/v5/order/create"
    params = {
        "category": "spot",
        "symbol": symbol,
        "side": "Buy",
        "orderType": "Market",
        "qty": quantity,
        "timeInForce": "IOC"
    }
    signed_params = _get_signed_params(params)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=signed_params) as response:
                data = await response.json()
                if data["retCode"] == 0:
                    return True
                else:
                    print(f"[ERROR] Order failed: {data}")
                    return False
    except Exception as e:
        print(f"[ERROR] place_spot_order: {e}")
        return False

async def get_balance():
    url = f"{BASE_URL}/v5/account/wallet-balance"
    params = {
        "accountType": "UNIFIED"
    }
    signed = _get_signed_params(params)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=signed) as response:
                return await response.json()
    except Exception as e:
        print(f"[ERROR] get_balance: {e}")
        return None

import requests
import time
import hmac
import hashlib
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

BASE_URL = "https://api.bybit.com"

def _get_headers(params, recv_window=5000):
    params["api_key"] = API_KEY
    params["recv_window"] = recv_window
    params["timestamp"] = int(time.time() * 1000)
    query_string = urlencode(sorted(params.items()))
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"), 
        bytes(query_string, "utf-8"), 
        hashlib.sha256
    ).hexdigest()
    params["sign"] = signature
    return params

def get_current_price(symbol: str) -> float:
    url = f"{BASE_URL}/v5/market/tickers"
    response = requests.get(url, params={"category": "spot", "symbol": symbol})
    data = response.json()
    try:
        return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None

def place_spot_order(symbol: str, side: str, usdt_amount: float = 200):
    price = get_current_price(symbol)
    if not price:
        return {"success": False, "error": "❌ Не удалось получить цену"}

    qty = round(usdt_amount / price, 6)  # округление зависит от конкретной пары

    url = f"{BASE_URL}/v5/order/create"
    params = {
        "category": "spot",
        "symbol": symbol,
        "side": side.capitalize(),
        "orderType": "Market",
        "qty": qty,
        "timeInForce": "IOC",
    }
    signed_params = _get_headers(params)
    response = requests.post(url, params=signed_params)
    data = response.json()

    if data.get("retCode") == 0:
        return {"success": True, "order_id": data["result"]["orderId"]}
    else:
        return {"success": False, "error": data.get("retMsg", "Unknown error")}

def get_balance():
    url = f"{BASE_URL}/v5/account/wallet-balance"
    params = {"accountType": "UNIFIED"}
    signed_params = _get_headers(params)
    response = requests.get(url, params=signed_params)
    return response.json()

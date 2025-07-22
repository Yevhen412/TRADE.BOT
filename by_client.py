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

#def get_current_price(symbol: str) -> float:
    url = f"{BASE_URL}/v5/market/tickers"
    response = requests.get(url, params={"category": "spot", "symbol": symbol})
    data = response.json()
    try:
        return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None

def place_spot_order(pair, side, amount):
    print(f"[FAKE ORDER] {side} {pair} на сумму {amount} USDT")
    return {
        "success": True,
        "order_id": "FAKE123456"
    }

def get_current_price(pair):
    # Возвращаем тестовую цену, например, 100.0
    print(f"[FAKE PRICE] Возвращаю цену 100.0 USDT для {pair}")
    return 100.0

def get_balance():
    url = f"{BASE_URL}/v5/account/wallet-balance"
    params = {"accountType": "UNIFIED"}
    signed_params = _get_headers(params)
    response = requests.get(url, params=signed_params)
    return response.json()

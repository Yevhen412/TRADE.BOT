import requests
import time
import hmac
import hashlib
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"


def _get_signed_params(params, recv_window=5000):
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


def place_spot_order(symbol, side, usdt_amount):
    """
    Размещает рыночный ордер на покупку/продажу на спотовом рынке (через Unified Account).
    """
    url = f"{BASE_URL}/v5/order/create"

    # Определяем, какая переменная требуется: qty или quoteQty
    # Для Buy на споте — указывается quoteQty (в USDT), для Sell — qty (в единицах актива)
    if side == "Buy":
        params = {
            "symbol": symbol,
            "side": "Buy",
            "orderType": "Market",
            "orderQty": None,  # не нужно
            "orderLinkId": f"long_{int(time.time())}",
            "isLeverage": 0,
            "qty": None,
            "quoteQty": usdt_amount
        }
    else:
        # Здесь требуется получить баланс токена для продажи (не реализовано пока)
        return {
            "success": False,
            "error": "Sell через spot пока не реализован"
        }

    signed_params = _get_signed_params(params)
    try:
        response = requests.post(url, data=signed_params)
        data = response.json()
        if data.get("retCode") == 0:
            return {
                "success": True,
                "order_id": data["result"]["orderId"]
            }
        else:
            return {
                "success": False,
                "error": data.get("retMsg", "Unknown error")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_current_price(symbol: str) -> float:
    """
    Возвращает текущую цену последней сделки по символу на споте.
    """
    url = f"{BASE_URL}/v5/market/tickers"
    try:
        response = requests.get(url, params={"category": "spot", "symbol": symbol})
        data = response.json()
        return float(data["result"]["list"][0]["lastPrice"])
    except:
        return None


def get_balance():
    """
    Получает баланс по Unified аккаунту.
    """
    url = f"{BASE_URL}/v5/account/wallet-balance"
    params = {
        "accountType": "UNIFIED"
    }
    signed = _get_signed_params(params)
    try:
        response = requests.get(url, params=signed)
        return response.json()
    except:
        return None

import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv
from telegram_notifier import send_telegram_message

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"

def generate_signature(params: dict, secret: str) -> str:
    sorted_params = dict(sorted((k, str(v)) for k, v in params.items() if v is not None))
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params.items())
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_spot_order(symbol: str, side: str, quote_qty: float, order_link_id: str):
    url = f"{BASE_URL}/v5/order/create"
    
    timestamp = str(int(time.time() * 1000))
    params = {
        "apiKey": API_KEY,
        "timestamp": timestamp,
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "quoteQty": quote_qty,
        "orderLinkId": order_link_id
        # ❌ "category": "spot" — не указываем!
    }

    signature = generate_signature(params, API_SECRET)
    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    params["sign"] = signature

    try:
        response = requests.post(url, json=params, headers=headers, timeout=10)
        response_data = response.json()

        if response_data.get("retCode") == 0:
            return True, response_data
        else:
            error_msg = response_data.get("retMsg", "Unknown error")
            return False, f"❌ Ошибка покупки {symbol}: {error_msg}"
    except Exception as e:
        return False, f"❌ Ошибка при отправке запроса: {e}"

async def connect_websocket(signal_data: dict):
    symbol = signal_data.get("symbol")
    order_link_id = f"long_{int(time.time())}"

    success, result = place_spot_order(symbol, "Buy", 200, order_link_id)
    
    if success:
        await send_telegram_message(f"✅ Покупка {symbol} выполнена успешно!")
    else:
        await send_telegram_message(str(result))


__all__ = ["connect_websocket"]

import os
import time
import hmac
import hashlib
import requests

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(params: dict, secret: str) -> str:
    ordered_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    print("🧩 Ordered params:", ordered_params)  # отладка
    signature = hmac.new(
        bytes(secret, "utf-8"),
        bytes(ordered_params, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    print("🔑 Signature:", signature)  # отладка
    return signature

def get_spot_balance():
    endpoint = "/v5/account/wallet-balance"
    url = BASE_URL + endpoint
    timestamp = get_timestamp()

    params = {
        "accountType": "SPOT",
        "timestamp": timestamp,
    }

    signature = sign(params, API_SECRET)

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
    }

    response = requests.get(url, headers=headers, params=params)
    
    print("🔵 Raw response:", response.text)
    print("📟 Status code:", response.status_code)

    try:
        return response.json()
    except Exception as e:
        print("❌ JSON error:", str(e))
        return {"error": response.text}

if __name__ == "__main__":
    print("🚀 Запрос баланса SPOT:")
    result = get_spot_balance()
    print("📊 Результат:", result)

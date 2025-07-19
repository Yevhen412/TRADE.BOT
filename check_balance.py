import os
import requests
import time
import hmac
import hashlib

# Получаем ключи из переменных окружения
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(params: dict) -> str:
    ordered_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    print(f"🔐 Ordered params: {ordered_params}")  # Отладка
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(ordered_params, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    print(f"🔑 Signature: {signature}")  # Отладка
    return signature

def get_balance(account_type: str):
    endpoint = "/v5/account/wallet-balance"
    url = BASE_URL + endpoint
    timestamp = get_timestamp()

    params = {
        "accountType": account_type,
        "timestamp": timestamp,
    }

    signature = sign(params)

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
    }

    print(f"📡 URL: {url}")
    print(f"📤 Headers: {headers}")
    print(f"📤 Params: {params}")

    response = requests.get(url, headers=headers, params=params)

    print(f"📥 Status code: {response.status_code}")
    print(f"📥 Raw response: {response.text}")

    try:
        return response.json()
    except Exception as e:
        print("⚠️ JSON parse error:", e)
        return {"error": response.text}

if __name__ == "__main__":
    print("🔎 Проверка баланса SPOT:")
    spot_result = get_balance("SPOT")
    print("📦 Ответ от API SPOT:", spot_result)

    print("\n🔎 Проверка баланса FUTURES (Unified):")
    futures_result = get_balance("UNIFIED")
    print("📦 Ответ от API FUTURES:", futures_result)

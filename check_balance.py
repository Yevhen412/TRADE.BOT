import os
import requests
import time
import hmac
import hashlib

# Получаем ключи из окружения
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"  # Убедись, что это не testnet

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(params: dict) -> str:
    ordered_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(ordered_params, "utf-8"),
        hashlib.sha256,
    ).hexdigest()

def get_spot_balance():
    endpoint = "/v5/account/wallet-balance"
    url = BASE_URL + endpoint
    timestamp = get_timestamp()

    params = {
        "accountType": "SPOT",
        "timestamp": timestamp,
    }

    signature = sign(params)

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data

def get_futures_balance():
    endpoint = "/v5/account/wallet-balance"
    url = BASE_URL + endpoint
    timestamp = get_timestamp()

    params = {
        "accountType": "UNIFIED",  # для USDT-фьючерсов (если Unified Account)
        "timestamp": timestamp,
    }

    signature = sign(params)

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return data

# Запускаем
if __name__ == "__main__":
    print("🔍 Проверка баланса SPOT:")
    spot = get_spot_balance()
    print(spot)

    print("\n🔍 Проверка баланса FUTURES (Unified):")
    fut = get_futures_balance()
    print(fut)

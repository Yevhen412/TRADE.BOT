import os
import requests
import time
import hmac
import hashlib

# Получаем ключи из окружения
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.bybit.com"  # Убедись, что это не testnet

print("🔐 API_KEY (первые 6 символов):", API_KEY[:6])
print("🔐 API_SECRET (первые 6 символов):", API_SECRET[:6])

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

    print("🔵 Raw response text (SPOT):", response.text)
    print("🔵 Status code (SPOT):", response.status_code)

    try:
        return response.json()
    except Exception as e:
        print("❌ Ошибка парсинга JSON (SPOT):", str(e))
        return {"error": response.text}

def get_futures_balance():
    endpoint = "/v5/account/wallet-balance"
    url = BASE_URL + endpoint
    timestamp = get_timestamp()

    params = {
        "accountType": "UNIFIED",  # Unified account (для фьючерсов USDT)
        "timestamp": timestamp,
    }

    signature = sign(params)

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
    }

    response = requests.get(url, headers=headers, params=params)

    print("🔵 Raw response text (FUTURES):", response.text)
    print("🔵 Status code (FUTURES):", response.status_code)

    try:
        return response.json()
    except Exception as e:
        print("❌ Ошибка парсинга JSON (FUTURES):", str(e))
        return {"error": response.text}

# Запускаем, если файл выполняется напрямую
if __name__ == "__main__":
    print("🔍 Проверка баланса SPOT:")
    response = get_spot_balance()
    print("🔧 Ответ от API SPOT:", response)

    print("\n🔍 Проверка баланса FUTURES (Unified):")
    response = get_futures_balance()
    print("🔧 Ответ от API FUTURES:", response)

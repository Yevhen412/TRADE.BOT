import os
import time
import hashlib
import hmac
import requests

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def get_unified_balance():
    print("🔍 Проверка баланса FUTURES (Unified):")

    url = "https://api.bybit.com/v5/account/wallet-balance"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    account_type = "UNIFIED"

    # Все параметры, которые пойдут в подпись и в запрос
    params = {
        "accountType": account_type,
        "timestamp": timestamp,
        "recvWindow": recv_window
    }

    # Строго по алфавиту
    ordered_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    print("🔐 Ordered params:", ordered_params)

    # Подпись
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(ordered_params, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    # Заголовки
    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    print("📡 Headers:", headers)

    response = requests.get(url, headers=headers, params=params)

    print("📦 Status code:", response.status_code)

    try:
        data = response.json()
        print("📬 Ответ от API:", data)
    except Exception as e:
        print("❌ Ошибка парсинга JSON:", str(e))
        print("📦 Raw response:", response.text)

if __name__ == "__main__":
    get_unified_balance()

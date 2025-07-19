import os
import time
import hmac
import hashlib
import requests

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def get_wallet_balance():
    url = "https://api.bybit.com/v5/account/wallet-balance"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    account_type = "UNIFIED"

    # 🚨 Порядок параметров ДОЛЖЕН быть строго как в строке подписи
    query_string = f"accountType={account_type}&recvWindow={recv_window}&timestamp={timestamp}"

    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    # 🟡 params ДОЛЖЕН быть идентичен query_string
    params = {
        "accountType": account_type,
        "recvWindow": recv_window,
        "timestamp": timestamp
    }

    print("🔐 Строка подписи:", query_string)
    print("🔏 Подпись:", signature)
    print("📤 Заголовки:", headers)
    print("📩 Параметры:", params)

    response = requests.get(url, headers=headers, params=params)
    print("📦 Статус:", response.status_code)

    try:
        print("📬 Ответ:", response.json())
    except Exception as e:
        print("❌ Ошибка JSON:", str(e))
        print("📄 Raw:", response.text)

if __name__ == "__main__":
    get_wallet_balance()

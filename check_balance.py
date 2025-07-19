import os
import time
import hmac
import hashlib
import requests

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

def get_unified_balance_post():
    print("🚀 Отправка POST-запроса в Bybit V5...")

    url = "https://api.bybit.com/v5/account/wallet-balance"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    account_type = "UNIFIED"

    body = {
        "accountType": account_type
    }

    # Строка запроса для подписи
    query_string = f"accountType={account_type}&timestamp={timestamp}&recvWindow={recv_window}"

    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(query_string, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    print("🧾 Headers:", headers)
    print("🛠️ Body:", body)
    print("🔐 Signature:", signature)

    response = requests.post(url, headers=headers, json=body)

    print("📦 Status code:", response.status_code)

    try:
        data = response.json()
        print("📬 Ответ от API:", data)
    except Exception as e:
        print("❌ Ошибка парсинга JSON:", str(e))
        print("📦 Raw response:", response.text)

if __name__ == "__main__":
    get_unified_balance_post()

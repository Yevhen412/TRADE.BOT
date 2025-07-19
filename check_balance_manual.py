import os
import time
import hashlib
import hmac
import requests
from dotenv import load_dotenv

load_dotenv()

# ⚙️ Ключи из окружения
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

# 🔁 Настройки
BASE_URL = "https://api.bybit.com"
ENDPOINT = "/v5/account/wallet-balance"
RECV_WINDOW = "5000"
ACCOUNT_TYPE = "UNIFIED"  # Или SPOT, если нужен спот

def get_timestamp():
    return str(int(time.time() * 1000))

def generate_signature(params: dict, secret: str) -> str:
    # Параметры должны быть отсортированы по ключу
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hmac.new(
        secret.encode("utf-8"),
        sorted_params.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def get_balance():
    timestamp = get_timestamp()

    # 🔒 Параметры запроса
    params = {
        "accountType": ACCOUNT_TYPE,
        "timestamp": timestamp,
        "recvWindow": RECV_WINDOW
    }

    signature = generate_signature(params, API_SECRET)

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": RECV_WINDOW
    }

    response = requests.get(BASE_URL + ENDPOINT, params=params, headers=headers)

    print("📦 Status Code:", response.status_code)
    try:
        print("📬 Response:", response.json())
    except Exception as e:
        print("❌ Error parsing response:", e)
        print("🔍 Raw text:", response.text)

if __name__ == "__main__":
    print("🔍 Checking real Bybit balance...")
    get_balance()

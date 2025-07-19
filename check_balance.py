from bybit import Bybit
import os

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = Bybit(api_key=api_key, api_secret=api_secret)

def get_wallet_balance():
    try:
        response = client.get_wallet_balance(accountType="UNIFIED")
        print("✅ Баланс:", response)
    except Exception as e:
        print("❌ Ошибка:", str(e))

if __name__ == "__main__":
    get_wallet_balance()

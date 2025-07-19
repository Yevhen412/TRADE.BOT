from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()
session = HTTP(
    testnet=False,
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)
response = session.get_wallet_balance(accountType="UNIFIED")
print("🔥 Баланс:", response)

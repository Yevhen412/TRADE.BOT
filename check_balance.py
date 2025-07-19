from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

# Загружаем ключи из переменных окружения
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# Инициализируем подключение к Bybit V5
session = HTTP(
    api_key=api_key,
    api_secret=api_secret
)

# Получаем баланс по аккаунту
response = session.get_wallet_balance(accountType="UNIFIED")

# Выводим результат
print("💰 Баланс:")
print(response)

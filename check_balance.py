from bybit import UnifiedMargin
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")

# Инициализируем соединение
client = UnifiedMargin(
    api_key=api_key,
    api_secret=api_secret,
    testnet=False  # True — если используешь testnet
)

# Получаем баланс
response = client.get_wallet_balance(accountType="UNIFIED")

# Показываем результат
print("🔥 Баланс:")
print(response)

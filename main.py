from check_balance import get_spot_balance, get_futures_balance

if __name__ == "__main__":
    print("🔍 Проверка баланса SPOT:")
    print(get_spot_balance())

    print("🔍 Проверка баланса FUTURES (Unified):")
    print(get_futures_balance())

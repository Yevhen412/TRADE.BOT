import os
from pybit.unified_trading import HTTP

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

session = HTTP(
    api_key=api_key,
    api_secret=api_secret
)

def place_market_order(symbol: str, side: str, qty: float):
    try:
        result = session.place_order(
            category="spot",         # или "linear" для фьючерсов
            symbol=symbol,
            side=side.upper(),       # "BUY" или "SELL"
            order_type="Market",
            qty=qty
        )
        return result
    except Exception as e:
        return {"error": str(e)}

import os
import telebot
from pybit.unified_trading import HTTP

# 🔐 Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

# 🤖 Telegram бот
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 📡 Bybit сессия
session = HTTP(api_key=API_KEY, api_secret=API_SECRET)

def get_usdt_balance():
    try:
        response = session.get_wallet_balance(accountType="UNIFIED")
        coins = response['result']['list'][0]['coin']
        for asset in coins:
            if asset['coin'] == 'USDT':
                wallet = asset['walletBalance']
                available = asset['availableToWithdraw']
                return f"💰 *Баланс USDT*\nВсего: `{wallet}`\nДоступно: `{available}`"
        return "USDT не найден в списке активов."
    except Exception as e:
        return f"Ошибка получения баланса: {str(e)}"

@bot.message_handler(commands=['balance'])
def send_balance(message):
    text = get_usdt_balance()
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == "__main__":
    print("🤖 Бот запущен")
    bot.infinity_polling()

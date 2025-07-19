import os
import telebot
from pybit.unified_trading import HTTP

# 📦 Загружаем переменные окружения
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Статичный ID получателя или берём из message.chat.id

# 🤖 Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 Сессия с Bybit
session = HTTP(api_key=API_KEY, api_secret=API_SECRET)

# 📊 Получаем баланс USDT
def get_usdt_balance():
    try:
        response = session.get_wallet_balance(accountType="UNIFIED")
        coins = response['result']['list'][0]['coin']
        for coin in coins:
            if coin['coin'] == 'USDT':
                return (
                    f"💰 *Баланс USDT:*\n"
                    f"Всего: `{coin['walletBalance']}`\n"
                    f"Доступно: `{coin['availableToWithdraw']}`"
                )
        return "❗ USDT не найден в кошельке."
    except Exception as e:
        return f"🚫 Ошибка получения баланса:\n`{str(e)}`"

# 📨 Команда Telegram
@bot.message_handler(commands=['balance'])
def send_balance(message):
    balance_info = get_usdt_balance()
    bot.send_message(message.chat.id, balance_info, parse_mode="Markdown")

# ▶️ Запуск
if __name__ == "__main__":
    print("✅ Бот запущен.")
    bot.infinity_polling()

import asyncio
import os
from telegram.ext import Application, CommandHandler, ContextTypes
from trade_simulator import TradeSimulator
from notifier import send_telegram_message

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

simulator = TradeSimulator()
bot_running = False

async def start_bot(update, context: ContextTypes.DEFAULT_TYPE):
    global bot_running
    if bot_running:
        await update.message.reply_text("⛔ Бот уже работает. Дождитесь завершения.")
        return

    bot_running = True
    await update.message.reply_text("✅ Бот запущен. Сессия длится 2 минуты...")

    async def session():
        try:
            await connect_ws(simulator)  # убедись, что эта функция реализована
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка WebSocket: {e}")

    task = asyncio.create_task(session())
    await asyncio.sleep(120)
    task.cancel()

    report = simulator.get_session_pnl_report()
    await send_telegram_message(report)

    bot_running = False

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_bot))
    app.run_polling()

if __name__ == "__main__":
    main()

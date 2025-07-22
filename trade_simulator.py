import time from by_client import place_spot_order, get_current_price from telegram_notifier import send_telegram_message

Условия сделки

ORDER_QUANTITY = 200  # USDT TAKE_PROFIT_PERCENT = 0.0045  # 0.45% STOP_LOSS_PERCENT = 0.002  # 0.2% COMMISSION = 0.0028  # 0.28% TRADE_COOLDOWN = 5  # секунд между сделками

active_trade = False last_trade_time = 0

async def process_signal(pair, current_price): global active_trade, last_trade_time

now = time.time()
if active_trade or now - last_trade_time < TRADE_COOLDOWN:
    return

# Покупка (лонг)
entry_price = current_price
take_profit_price = entry_price * (1 + TAKE_PROFIT_PERCENT)
stop_loss_price = entry_price * (1 - STOP_LOSS_PERCENT)

try:
    order_result = place_spot_order(pair, 'Buy', ORDER_QUANTITY)
    if not order_result['success']:
        await send_telegram_message(f"❌ Не удалось купить {pair}: {order_result['error']}")
        return

    active_trade = True
    last_trade_time = now
    await send_telegram_message(
        f"🟢 Покупка {pair} по {entry_price:.4f} (TP: {take_profit_price:.4f}, SL: {stop_loss_price:.4f})"
    )

    # Мониторинг позиции
    while True:
        current_price = get_current_price(pair)

        if current_price >= take_profit_price:
            pnl = (take_profit_price - entry_price) * (ORDER_QUANTITY / entry_price)
            net = pnl - (ORDER_QUANTITY * COMMISSION)
            await send_telegram_message(
                f"✅ Тейк профит достигнут по {pair} — цена {current_price:.4f}\nЧистая прибыль: {net:.4f} USDT"
            )
            break

        elif current_price <= stop_loss_price:
            pnl = (stop_loss_price - entry_price) * (ORDER_QUANTITY / entry_price)
            net = pnl - (ORDER_QUANTITY * COMMISSION)
            await send_telegram_message(
                f"❌ Стоп-лосс сработал по {pair} — цена {current_price:.4f}\nУбыток: {net:.4f} USDT"
            )
            break

        await asyncio.sleep(1)

except Exception as e:
    await send_telegram_message(f"❗ Ошибка при обработке сделки: {e}")

finally:
    active_trade = False


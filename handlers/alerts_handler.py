from aiogram import Router, types, F
from aiogram.filters import Command
from services.database import save_alert, get_user_alerts, delete_alert
import keyboards.keyboards as kb

router = Router()

@router.message(Command("set_alert"))
async def set_alert_command(message: types.Message):
    args = message.text.split()
    
    if len(args) != 3:
        await message.answer("❌ Использование: `/set_alert BTCUSDT 45000`", parse_mode="Markdown")
        return

    pair = args[1].upper()
    try:
        target_price = float(args[2])
    except ValueError:
        await message.answer("❌ Неверный формат цены. Пример: `/set_alert BTCUSDT 45000`", parse_mode="Markdown")
        return

    save_alert(message.from_user.id, pair, target_price)
    await message.answer(f"✅ Уведомление установлено: {pair} {target_price} USDT", parse_mode="Markdown")

@router.message(Command("my_alerts"))
async def my_alerts_command(message: types.Message):
    alerts = get_user_alerts(message.from_user.id)
    
    if not alerts:
        await message.answer("📭 У вас нет активных уведомлений.")
        return

    response = "🔔 *Ваши активные уведомления:*\n"
    for pair, target_price in alerts:
        response += f"• {pair} → {target_price} USDT\n"

    await message.answer(response, reply_markup=kb.get_alerts_keyboard(alerts), parse_mode="Markdown")

@router.callback_query(F.data.startswith("delete_alert_"))
async def delete_alert_handler(call: types.CallbackQuery):
    pair = call.data.replace("delete_alert_", "", 1)  
    delete_alert(call.from_user.id, pair)

    await call.message.edit_text(f"✅ Уведомление для {pair} удалено!", parse_mode="Markdown")

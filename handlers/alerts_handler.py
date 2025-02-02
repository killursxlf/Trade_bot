from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from services.database import save_alert, get_user_alerts, delete_alert
from aiogram.fsm.state import State, StatesGroup
import keyboards.keyboards as kb

router = Router()

class FormState(StatesGroup):
    waiting_for_alert = State()


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

    if alerts:
        response = "🔔 *Ваши активные уведомления:*\n"
        for pair, target_price in alerts:
            response += f"• {pair} → {target_price} USDT\n"
    else:
        response = "📭 У вас нет активных уведомлений. Хотите добавить?"

    await message.answer(
        response,
        reply_markup=kb.get_alerts_keyboard(alerts),  
        parse_mode="Markdown"
    )

@router.callback_query(lambda call: call.data.startswith("delete_alert_"))
async def delete_alert_handler(call: types.CallbackQuery):
    
    data = call.data.split("_")  

    if len(data) < 3:
        await call.answer("❌ Ошибка: неверный формат данных.")
        return

    print(f"Received data: {data}") 
    _, _, pair, price = data  

    delete_alert(call.from_user.id, pair, price)  

    await call.message.edit_text(
        f"✅ Уведомление для {pair} удалено!"  
    )

@router.callback_query(lambda call: call.data == "add_alert")
async def add_alert_button_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer() 
    await call.message.answer("Введите валютную пару и цену для нового алерта (пример: BTCUSDT 45000):")
    await state.set_state(FormState.waiting_for_alert)  

@router.message(FormState.waiting_for_alert)
async def set_alert_command(message: types.Message, state: FSMContext):
    data = message.text.split()
    if len(data) != 2:
        await message.answer("❌ Неверный формат. Введите в формате: BTCUSDT 45000")
        return

    pair, price = data[0].upper(), data[1]
    save_alert(message.from_user.id, pair, price)  

    await message.answer(f"✅ Алерт установлен: {pair} при {price} USDT")
    await state.clear()  
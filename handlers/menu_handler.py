from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.balance_handler import balance_reply
from handlers.currency_handler import currency_pair_reply
from handlers.volume_handler import top_volume_command
from handlers.hot_handler import hot_coins_command
from services.database import get_user_alerts
import keyboards.keyboards as kb

router = Router()

@router.message(Command("menu"))
async def show_inline_menu(message: types.Message):
    await message.reply("📌 Главное меню:", reply_markup=kb.main_menu_keyboard)

@router.message(lambda message: message.text == "📊 Просмотр баланса")
async def balance_button_handler(message: types.Message):
    await balance_reply(message)  

@router.message(lambda message: message.text == "💱 Просмотр валютной пары")
async def currency_button_handler(message: types.Message, state: FSMContext):
    await currency_pair_reply(message, state)  

@router.message(lambda message: message.text == "❌ Выход")
async def exit_button_handler(message: types.Message):
    await message.reply("👋 Вы вышли из меню.", reply_markup=types.ReplyKeyboardRemove())

@router.callback_query(F.data == "view_balance")
async def inline_balance_handler(call: types.CallbackQuery):
    await balance_reply(call.message)  

@router.callback_query(F.data == "view_currency_pair")
async def inline_currency_handler(call: types.CallbackQuery, state: FSMContext):
    await currency_pair_reply(call.message, state)  
    
@router.callback_query(F.data == "exit_menu")
async def inline_exit_handler(call: types.CallbackQuery):
    await call.message.answer("👋 Вы вышли из меню.", reply_markup=types.ReplyKeyboardRemove())

@router.callback_query(F.data == "view_alerts")
async def inline_my_alerts(call: types.CallbackQuery):
    alerts = get_user_alerts(call.from_user.id)

    if not alerts:
        await call.message.edit_text("📭 У вас нет активных уведомлений.", parse_mode="Markdown")
        return

    response = "🔔 *Ваши активные уведомления:*\n"
    for pair, target_price in alerts:
        response += f"• {pair} → {target_price} USDT\n"

    await call.message.edit_text(response, reply_markup=kb.get_alerts_keyboard(alerts), parse_mode="Markdown")

@router.message(lambda message: message.text == "🔔 Мои уведомления")
async def reply_my_alerts(message: types.Message):
    alerts = get_user_alerts(message.from_user.id)

    if not alerts:
        await message.answer("📭 У вас нет активных уведомлений.", parse_mode="Markdown")
        return

    response = "🔔 *Ваши активные уведомления:*\n"
    for pair, target_price in alerts:
        response += f"• {pair} → {target_price} USDT\n"

    await message.answer(response, reply_markup=kb.get_alerts_keyboard(alerts), parse_mode="Markdown")

@router.callback_query(F.data == "view_hot_coins")
async def inline_hot_coins_handler(call: types.CallbackQuery):
    await hot_coins_command(call.message)

@router.callback_query(F.data == "view_top_volume")
async def inline_top_volume_handler(call: types.CallbackQuery):
    await top_volume_command(call.message)

@router.message(lambda message: message.text == "🔥 ТОП-5 волатильных")
async def reply_hot_coins_handler(message: types.Message):
    await hot_coins_command(message)

@router.message(lambda message: message.text == "📊 ТОП-5 по объёму")
async def reply_top_volume_handler(message: types.Message):
    await top_volume_command(message)


from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
import keyboards.keyboards as kb
from services.binance_service import get_trade_data

router = Router()

class FormState(StatesGroup):
    waiting_for_currency_pair = State()

@router.message(Command("currency"))
async def currency_pair_reply(message: types.Message, state: FSMContext):
    await message.reply("Введите валютную пару (например, BTCUSDT):")
    await state.set_state(FormState.waiting_for_currency_pair)

@router.message(FormState.waiting_for_currency_pair)
async def handle_currency_pair(message: types.Message, state: FSMContext):
    pair = message.text.strip().upper()
    await state.update_data(pair=pair)
    await message.reply("📅 Выберите временной промежуток:", reply_markup=kb.get_timeframe_keyboard(pair))

@router.callback_query(lambda call: call.data.startswith("timeframe_"))
async def handle_timeframe_selection(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    pair = user_data.get("pair")

    timeframe = call.data.split("_")[1]
    trade_data = get_trade_data(call.from_user.id, pair, timeframe)

    if trade_data:
        await call.message.edit_text(
            text=f"""📈 *{pair}*
💰 *Текущая цена:* {trade_data['current_price']}
📊 *Макс. цена:* {trade_data['high_price']}
📉 *Мин. цена:* {trade_data['low_price']}
🔄 *Объём торгов:* {trade_data['volume']}
💵 *Объём в USDT:* {trade_data['volume_usdt']}""",
            parse_mode="Markdown"  
        )
    await state.clear()

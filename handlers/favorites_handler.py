from aiogram import Router, types
from aiogram.filters import Command
from services.database import save_favorite, get_favorites, delete_favorite
from services.binance_service import get_fav_data
import keyboards.keyboards as kb

router = Router()

@router.message(Command("add_favorite"))
async def add_favorite_command(message: types.Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: `/add_favorite BTCUSDT`", parse_mode="Markdown")
        return

    pair = args[1].upper()
    save_favorite(message.from_user.id, pair)
    await message.answer(f"✅ {pair} добавлен в избранное!", parse_mode="Markdown")

@router.message(Command("favorites"))
@router.callback_query(lambda call: call.data == "view_favorites")
async def show_favorites_command(event: types.Message | types.CallbackQuery):  
    user_id = event.from_user.id  
       
    favorites = get_favorites(user_id)
    
    if not favorites:
        if isinstance(event, types.Message):
            await event.answer("📌 У вас нет избранных монет.")
        else:
            await event.message.edit_text("📌 У вас нет избранных монет.")
        return

    keyboard = kb.get_favorites_keyboard(favorites)
    
    if isinstance(event, types.Message):
        await event.answer("📌 *Ваши избранные монеты:*", reply_markup=keyboard, parse_mode="Markdown")
    else:
        await event.message.edit_text("📌 *Ваши избранные монеты:*", reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(lambda call: call.data.startswith("delete_favorite_"))
async def delete_favorite_handler(call: types.CallbackQuery):
    pair = call.data.replace("delete_favorite_", "", 1)
    delete_favorite(call.from_user.id, pair)

    await call.message.edit_text(f"✅ {pair} удалён из избранного!", parse_mode="Markdown")

@router.callback_query(lambda call: call.data.startswith("view_fav_"))
async def view_favorite_handler(call: types.CallbackQuery):
    pair = call.data.replace("view_fav_", "", 1)

    trade_data = get_fav_data(pair, "24h")  
    
    if "error" in trade_data:
        await call.answer(f"Ошибка: {trade_data['error']}")
        return

    response = (
        f"📊 *{pair}*\n"
        f"💰 Цена: {trade_data['current_price']} USDT\n"
        f"📈 Макс: {trade_data['high_price']} USDT\n"
        f"📉 Мин: {trade_data['low_price']} USDT\n"
        f"📊 Объём: {float(trade_data['volume']):,.2f} USDT"
    )

    await call.message.edit_text(response, reply_markup=kb.get_favorites_keyboard(get_favorites(call.from_user.id)), parse_mode="Markdown")



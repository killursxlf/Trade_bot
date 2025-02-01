from aiogram import Router, types
from aiogram.filters import Command
from services.database import save_favorite, get_favorites
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
async def show_favorites_command(message: types.Message):
    favorites = get_favorites(message.from_user.id)
    if not favorites:
        await message.answer("📌 У вас нет избранных монет.")
        return

    keyboard = kb.get_favorites_keyboard(favorites)
    await message.answer("📌 Ваши избранные монеты:", reply_markup=keyboard)

from aiogram import Router, types
from aiogram.filters import Command
from services.binance_service import get_balance

router = Router()

@router.message(Command("balance"))
async def balance_reply(message: types.Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)

    if balance is None:
        await message.reply("⚠️ Сначала авторизуйтесь: /authorize")
    else:
        await message.reply(f"💰 Ваш баланс USDT: {balance}")

from aiogram import Router, types
from aiogram.filters import Command
from services.binance_service import get_full_balance

router = Router()

@router.message(Command("balance"))
async def balance_reply(message: types.Message):
    user_id = message.from_user.id
    balance_data = get_full_balance(user_id)

    if not balance_data:
        await message.answer("❌ Не удалось получить баланс. Проверьте API-ключи.")
        return

    assets, total_balance_usdt = balance_data

    response = "💰 *Ваш баланс:*\n"
    for asset, amount, usdt_value in assets:
        response += f"🔹 {asset}: {amount:.6f} (~{usdt_value:.2f} USDT)\n"

    response += f"\n💵 *Общая стоимость всех активов:* {total_balance_usdt:.2f} USDT"

    await message.answer(response, parse_mode="Markdown")

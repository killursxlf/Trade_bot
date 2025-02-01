from aiogram import Router, types
from aiogram.filters import Command
from binance.client import Client

router = Router()

@router.message(Command("hot_coins"))
async def hot_coins_command(message: types.Message):
    client = Client()

    tickers = client.get_ticker()
    usdt_pairs = [t for t in tickers if t['symbol'].endswith("USDT")]

    hot_tickers = sorted(usdt_pairs, key=lambda x: (float(x['highPrice']) - float(x['lowPrice'])), reverse=True)

    unique_coins = []
    hot_unique = []
    
    for ticker in hot_tickers:
        coin = ticker['symbol'].replace("USDT", "")
        if coin not in unique_coins:
            unique_coins.append(coin)
            hot_unique.append(ticker)
        if len(hot_unique) >= 5:
            break

    response = "🔥 *ТОП-5 волатильных монет за 24 часа:*\n"
    for idx, ticker in enumerate(hot_unique, start=1):
        volatility = float(ticker['highPrice']) - float(ticker['lowPrice'])
        response += f"{idx}️⃣ {ticker['symbol']} → Разница: {volatility:.2f} USDT\n"

    await message.answer(response, parse_mode="Markdown")

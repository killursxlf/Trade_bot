from aiogram import Router, types
from aiogram.filters import Command
from binance.client import Client

router = Router()

@router.message(Command("top_coins"))
async def top_coins_command(message: types.Message):
    client = Client()

    tickers = client.get_ticker()
    usdt_pairs = [t for t in tickers if t['symbol'].endswith("USDT")]

    top_tickers = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)

    unique_coins = []
    top_unique = []
    
    for ticker in top_tickers:
        coin = ticker['symbol'].replace("USDT", "")  
        if coin not in unique_coins:  
            unique_coins.append(coin)
            top_unique.append(ticker)
        if len(top_unique) >= 5:  
            break

    response = "🔥 *ТОП-5 монет (только к USDT) за 24 часа:*\n"
    for idx, ticker in enumerate(top_unique, start=1):
        response += f"{idx}️⃣ {ticker['symbol']} → +{ticker['priceChangePercent']}%\n"

    await message.answer(response, parse_mode="Markdown")

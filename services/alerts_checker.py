import asyncio
from aiogram import Bot
from binance.client import Client
from services.database import get_alerts, delete_alert, get_api_keys

async def check_alerts(bot: Bot):
    last_prices = {} 

    while True:
        alerts = get_alerts()
        
        for user_id, pair, target_price in alerts:
            api_keys = get_api_keys(user_id)
            if not api_keys:
                continue  

            api_key, api_secret = api_keys
            client = Client(api_key, api_secret)

            try:
                ticker = client.get_ticker(symbol=pair)
                current_price = float(ticker['lastPrice'])

                last_price = last_prices.get(pair, current_price)  

                
                if last_price < target_price <= current_price:  
                    await bot.send_message(user_id, f"🚀 *Цена достигла цели!* {pair}: {current_price} USDT", parse_mode="Markdown")

                elif last_price > target_price >= current_price:  
                    await bot.send_message(user_id, f"📉 *Цена упала ниже цели!* {pair}: {current_price} USDT", parse_mode="Markdown")

                last_prices[pair] = current_price  

            except Exception as e:
                print(f"Ошибка при проверке уведомления {pair}: {e}")

        await asyncio.sleep(60)  

from binance.client import Client

user_data = {}

def get_balance(user_id):

    if user_id not in user_data:
        return None
    
    client = Client(user_data[user_id]['api_key'], user_data[user_id]['api_secret'])

    try:
        balance = client.get_asset_balance(asset='USDT')
        return balance['free'] if balance else "0.0"
    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return None

def get_trade_data(user_id, pair, interval):
    if user_id not in user_data:
        return None
    
    client = Client(user_data[user_id]['api_key'], user_data[user_id]['api_secret'])

    try:
        ticker = client.get_ticker(symbol=pair)
        current_price = float(ticker.get('lastPrice', 0))

        interval_map = {
            "4h": "4h", "8h": "8h", "12h": "12h", "24h": "1d",
            "3d": "3d", "1w": "1w", "1m": "1M"
        }
        binance_interval = interval_map.get(interval)

        if not binance_interval:
            return {"error": "Неподдерживаемый интервал"}

        klines = client.get_klines(symbol=pair, interval=binance_interval, limit=1)
        if not klines:
            return {"error": "Нет данных"}

        high_price = float(klines[0][2])   
        low_price = float(klines[0][3])    
        volume = float(klines[0][5])       


        average_price = (high_price + low_price) / 2
        volume_usdt = round(volume * average_price, 2)

        return {
            "current_price": current_price,
            "high_price": high_price,
            "low_price": low_price,
            "volume": volume,         
            "volume_usdt": volume_usdt  
        }

    except Exception as e:
        print(f"Ошибка получения данных о торговле: {e}")
        return {"error": "Ошибка Binance API"}

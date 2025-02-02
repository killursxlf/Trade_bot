from binance.client import Client
from services.database import get_api_keys
import pandas as pd
import talib
    
def get_full_balance(user_id):
    api_keys = get_api_keys(user_id)
    if not api_keys:
        return None
    
    api_key, api_secret = api_keys
    client = Client(api_key, api_secret)

    try:
        account_info = client.get_account()
        
        tickers = {t["symbol"]: float(t["price"]) for t in client.get_ticker() if "price" in t}

        assets = []
        total_balance_usdt = 0.0

        for asset in account_info["balances"]:
            asset_name = asset["asset"]
            free_balance = float(asset["free"])
            locked_balance = float(asset["locked"])
            total_balance = free_balance + locked_balance

            if total_balance > 0:
                if asset_name == "USDT":  
                    balance_in_usdt = total_balance
                else:
                    symbol = asset_name + "USDT"
                    balance_in_usdt = total_balance * tickers.get(symbol, 0)  

                total_balance_usdt += balance_in_usdt
                assets.append((asset_name, total_balance, balance_in_usdt))

        assets.sort(key=lambda x: x[2], reverse=True)

        return assets, total_balance_usdt

    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return None

def get_trade_data(user_id, pair, interval):
    api_keys = get_api_keys(user_id)
    if not api_keys:
        return None
    
    api_key, api_secret = api_keys
    client = Client(api_key, api_secret)

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

def get_fav_data(pair, interval="24h"):
    client = Client()

    try:
        ticker = client.get_ticker(symbol=pair)
        klines = client.get_klines(symbol=pair, interval="1d", limit=1)  

        last_price = float(ticker.get('lastPrice', '0'))
        volume_in_coins = float(klines[0][5])  
        volume_in_usdt = volume_in_coins * last_price 

        return {
            "current_price": last_price,
            "high_price": klines[0][2],  
            "low_price": klines[0][3],   
            "volume": volume_in_usdt    
        }

    except Exception as e:
        print(f"Ошибка получения данных о {pair}: {e}")
        return {"error": "Ошибка Binance API"}

def get_ta_data(user_id, pair, interval, limit=500):

    api_keys = get_api_keys(user_id)
    if not api_keys:
        return {"error": "Пользователь не авторизован"}

    api_key, api_secret = api_keys
    client = Client(api_key, api_secret)

    try:
        klines = client.get_klines(symbol=pair, interval=interval, limit=limit)
        
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        df['SMA_50'] = talib.SMA(df['close'], timeperiod=50)
        df['EMA_20'] = talib.EMA(df['close'], timeperiod=20)    

        macd, macd_signal, macd_hist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'] = macd
        df['MACD_signal'] = macd_signal
        df['MACD_hist'] = macd_hist

        upperband, middleband, lowerband = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df['BB_upper'] = upperband
        df['BB_middle'] = middleband
        df['BB_lower'] = lowerband
        
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        
        df['OBV'] = talib.OBV(df['close'], df['volume'])
        
        df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
        
        latest = df.iloc[-1].to_dict()
        
        rsi = latest.get("RSI")
        if rsi is None:
            zone = "Нет данных для RSI"
        elif rsi > 70:
            zone = "Перекупленность"
        elif rsi < 30:
            zone = "Перепроданность"
        else:
            zone = "Нейтральная зона"
        
        return {
            "pair": pair,
            "interval": interval,
            "last_close": latest.get("close"),
            "RSI": latest.get("RSI"),
            "SMA_50": latest.get("SMA_50"),
            "EMA_20": latest.get("EMA_20"),
            "MACD": latest.get("MACD"),
            "MACD_signal": latest.get("MACD_signal"),
            "MACD_hist": latest.get("MACD_hist"),
            "BB_upper": latest.get("BB_upper"),
            "BB_middle": latest.get("BB_middle"),
            "BB_lower": latest.get("BB_lower"),
            "ATR": latest.get("ATR"),
            "OBV": latest.get("OBV"),
            "ADX": latest.get("ADX"),
            "zone": zone
        }
    
    except Exception as e:
        print(f"Ошибка получения данных для TA: {e}")
        return {"error": "Ошибка получения данных для TA"}

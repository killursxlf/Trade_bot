from binance.client import Client
from services.database import get_api_keys

def get_full_balance(user_id):
    """Получает ВСЕ активы пользователя с переводом в USDT."""
    api_keys = get_api_keys(user_id)
    if not api_keys:
        return None
    
    api_key, api_secret = api_keys
    client = Client(api_key, api_secret)

    try:
        account_info = client.get_account()
        
        # ✅ Фильтруем только те данные, где есть "price"
        tickers = {t["symbol"]: float(t["price"]) for t in client.get_ticker() if "price" in t}

        assets = []
        total_balance_usdt = 0.0

        for asset in account_info["balances"]:
            asset_name = asset["asset"]
            free_balance = float(asset["free"])
            locked_balance = float(asset["locked"])
            total_balance = free_balance + locked_balance

            if total_balance > 0:
                if asset_name == "USDT":  # Если это USDT, не нужно конвертировать
                    balance_in_usdt = total_balance
                else:
                    symbol = asset_name + "USDT"
                    balance_in_usdt = total_balance * tickers.get(symbol, 0)  # ✅ Если цены нет, используем 0

                total_balance_usdt += balance_in_usdt
                assets.append((asset_name, total_balance, balance_in_usdt))

        # Сортируем активы по убыванию баланса в USDT
        assets.sort(key=lambda x: x[2], reverse=True)

        return assets, total_balance_usdt

    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return None

def get_trade_data(user_id, pair, interval):
    """Получение информации о валютной паре"""
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

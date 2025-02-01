import sqlite3

DB_NAME = "tradebot.db"

def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                api_key TEXT NOT NULL,
                api_secret TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                user_id INTEGER,
                pair TEXT,
                target_price REAL,
                PRIMARY KEY (user_id, pair)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                pair TEXT,
                PRIMARY KEY (user_id, pair)
            )
        ''')
        conn.commit()

def save_alert(user_id: int, pair: str, target_price: float):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO alerts (user_id, pair, target_price)
            VALUES (?, ?, ?)
        ''', (user_id, pair, target_price))
        conn.commit()

def get_alerts():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, pair, target_price FROM alerts')
        return cursor.fetchall()

def save_api_keys(user_id: int, api_key: str, api_secret: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, api_key, api_secret)
            VALUES (?, ?, ?)
        ''', (user_id, api_key, api_secret))
        conn.commit()

def get_api_keys(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT api_key, api_secret FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result if result else None 

def get_user_alerts(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pair, target_price FROM alerts WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

def delete_alert(user_id: int, pair: str, target_price: float):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alerts WHERE user_id = ? AND pair = ? AND target_price = ?', (user_id, pair, target_price))
        conn.commit()

def save_favorite(user_id: int, pair: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO favorites (user_id, pair)
            VALUES (?, ?)
        ''', (user_id, pair))
        conn.commit()

def get_favorites(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pair FROM favorites WHERE user_id = ?', (user_id,))
        result = cursor.fetchall()

    return [row[0] for row in result]

def delete_favorite(user_id: int, pair: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND pair = ?', (user_id, pair))
        conn.commit()

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Просмотр баланса", callback_data="view_balance")],
        [InlineKeyboardButton(text="💱 Просмотр валютной пары", callback_data="view_currency_pair")],
        [InlineKeyboardButton(text="🔥 ТОП-5 волатильных", callback_data="view_hot_coins")],
        [InlineKeyboardButton(text="📊 ТОП-5 по объёму", callback_data="view_top_volume")],
        [InlineKeyboardButton(text="❌ Выход", callback_data="exit_menu")]
    ]
)

persistent_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Просмотр баланса"), KeyboardButton(text="💱 Просмотр валютной пары")],
        [KeyboardButton(text="🔥 ТОП-5 волатильных"), KeyboardButton(text="📊 ТОП-5 по объёму")],
        [KeyboardButton(text="🔔 Мои уведомления"), KeyboardButton(text="❌ Выход")]
    ],
    resize_keyboard=True
)


authorize_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔑 Авторизоваться", callback_data="authorize")]
])

def get_timeframe_keyboard(pair):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="4H", callback_data=f"timeframe_4h_{pair}")],
        [InlineKeyboardButton(text="8H", callback_data=f"timeframe_8h_{pair}")],
        [InlineKeyboardButton(text="12H", callback_data=f"timeframe_12h_{pair}")],
        [InlineKeyboardButton(text="24H", callback_data=f"timeframe_24h_{pair}")],
        [InlineKeyboardButton(text="3D", callback_data=f"timeframe_3d_{pair}")],
        [InlineKeyboardButton(text="1W", callback_data=f"timeframe_1w_{pair}")],
        [InlineKeyboardButton(text="1M", callback_data=f"timeframe_1m_{pair}")]
    ])

def get_alerts_keyboard(alerts):

    keyboard = [
        [InlineKeyboardButton(text=f"❌ Удалить {pair}", callback_data=f"delete_alert_{pair}")] 
        for pair, _ in alerts
    ] 
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

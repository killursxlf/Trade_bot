import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from binance.client import Client
from config import API_TOKEN  # Импортируем токен из config.py

# Настроим логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot_logs.log"),
        logging.StreamHandler()
    ]
)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Логгер
logger = logging.getLogger(__name__)

# Пример хранилища API ключей для пользователей
user_data = {}

# Определим состояния через StatesGroup
class FormState(StatesGroup):
    waiting_for_api_keys = State()
    waiting_for_currency_pair = State()

# Главная клавиатура для меню пользователя
def get_main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Просмотр баланса")],
            [KeyboardButton("Просмотр валютной пары")],
            [KeyboardButton("Выход")]
        ],
        resize_keyboard=True
    )
    return keyboard


# Начальная команда
@dp.message(Command("start"))
async def start(message: types.Message):
    """
    Обработчик команды /start.
    """
    await message.reply("Привет! Введите команду /authorize для ввода вашего Binance API ключа.")

# Команда для начала авторизации
@dp.message(Command("authorize"))
async def authorize(message: types.Message, state: FSMContext):
    """
    Запрос API ключей от пользователя.
    """
    user_id = message.from_user.id
    await message.reply("Введите ваш Binance API ключ и секретный ключ через пробел (например, <API-KEY> <SECRET-KEY>):")
    
    # Переходим в состояние ожидания ключей
    await state.set_state(FormState.waiting_for_api_keys)

# Обработка ввода API ключей
@dp.message(FormState.waiting_for_api_keys)
async def handle_binance_api_keys(message: types.Message, state: FSMContext):
    """
    Обрабатывает получение API ключей от пользователя.
    """
    user_id = message.from_user.id

    # Проверяем, что сообщение содержит два ключа через пробел
    keys = message.text.split()
    if len(keys) != 2:
        await message.reply("Неверный формат. Пожалуйста, отправьте ключи в формате: <API-KEY> <SECRET-KEY>")
        return
    
    api_key, api_secret = keys

    # Проверим API ключи с помощью Binance API
    try:
        client = Client(api_key, api_secret)
        # Пытаемся получить аккаунт пользователя, чтобы проверить ключи
        account = client.get_account()
        
        # Сохраняем ключи для дальнейшего использования
        user_data[user_id] = {
            'api_key': api_key,
            'api_secret': api_secret
        }

        await message.reply(f"Авторизация прошла успешно! Ваш аккаунт: {account['accountType']}.")
        logger.info(f"User {user_id} successfully authorized with Binance.")
        
        # Завершаем состояние, так как ключи получили
        await state.clear()

    except Exception as e:
        await message.reply("Ошибка авторизации! Проверьте правильность введенных ключей.")
        logger.error(f"User {user_id} failed to authorize: {str(e)}")

# Команда для отображения меню
@dp.message(Command("menu"))
async def show_menu(message: types.Message):
    """
    Показывает главное меню пользователя.
    """
    await message.reply("Выберите действие:", reply_markup=get_main_menu_keyboard())

# Обработка кнопки "Просмотр баланса"
@dp.message(lambda message: message.text == "Просмотр баланса")
async def balance(message: types.Message):
    """
    Получаем баланс пользователя из Binance после авторизации.
    """
    user_id = message.from_user.id
    if user_id not in user_data or 'api_key' not in user_data[user_id]:
        await message.reply("Пожалуйста, авторизуйтесь с помощью команды /authorize.")
        return

    # Получаем сохраненные ключи пользователя
    api_key = user_data[user_id]['api_key']
    api_secret = user_data[user_id]['api_secret']

    # Пытаемся подключиться к API Binance
    try:
        client = Client(api_key, api_secret)
        balance = client.get_asset_balance(asset='USDT')  # Пример для USDT, можно заменить на другую валюту
        if balance:
            await message.reply(f"Ваш баланс {balance['asset']}: {balance['free']}")
        else:
            await message.reply("Не удалось получить баланс.")
    except Exception as e:
        await message.reply("Ошибка при получении баланса. Проверьте свои ключи.")
        logger.error(f"Error fetching balance for user {user_id}: {str(e)}")

# Обработка кнопки "Просмотр валютной пары"
@dp.message(lambda message: message.text == "Просмотр валютной пары")
async def view_currency_pair(message: types.Message, state: FSMContext):
    """
    Запросить пользователю валютную пару и показать информацию.
    """
    await message.reply("Введите валютную пару (например, BTCUSDT):")
    
    # Устанавливаем состояние ожидания валютной пары
    await state.set_state(FormState.waiting_for_currency_pair)

# Обработка ввода валютной пары
@dp.message(FormState.waiting_for_currency_pair)
async def handle_currency_pair(message: types.Message, state: FSMContext):
    """
    Обрабатывает получение валютной пары от пользователя.
    """
    user_id = message.from_user.id
    pair = message.text.strip().upper()

    # Проверяем, что пара состоит из двух валют
    if len(pair) < 5:
        await message.reply("Неверный формат валютной пары. Попробуйте снова (например, BTCUSDT).")
        return

    # Получаем информацию о валютной паре
    try:
        client = Client(user_data[user_id]['api_key'], user_data[user_id]['api_secret'])
        ticker = client.get_ticker(symbol=pair)
        
        if ticker:
            await message.reply(f"Текущая цена для {pair}: {ticker['lastPrice']}")
        else:
            await message.reply(f"Не удалось получить информацию для валютной пары {pair}.")
    except Exception as e:
        await message.reply(f"Ошибка при получении данных для валютной пары {pair}: {str(e)}")
    
    # Завершаем состояние
    await state.clear()

# Обработка кнопки "Выход"
@dp.message(lambda message: message.text == "Выход")
async def exit_menu(message: types.Message):
    """
    Завершает текущую сессию и выводит пользователя из меню.
    """
    await message.reply("Выход из меню. Чтобы снова авторизоваться, используйте команду /authorize.", reply_markup=types.ReplyKeyboardRemove())

# Запуск бота
async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот был остановлен.")

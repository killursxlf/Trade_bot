from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from binance.client import Client
import keyboards.keyboards as kb
from services.database import save_api_keys, get_api_keys  # ✅ Импорт работы с БД

router = Router()

class FormState(StatesGroup):
    waiting_for_api_keys = State()

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_data = get_api_keys(user_id)  # ✅ Проверяем, есть ли ключи в БД

    if user_data:
        await message.answer("✅ Вы уже авторизованы! Можете пользоваться ботом.", reply_markup=kb.persistent_menu_keyboard)
    else:
        await message.answer("👋 Привет! Используйте кнопку ниже для авторизации.", reply_markup=kb.authorize_keyboard)

@router.message(Command("authorize"))
async def authorize_command(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш Binance API ключ и секрет через пробел:")
    await state.set_state(FormState.waiting_for_api_keys)

@router.callback_query(lambda call: call.data == "authorize")
async def authorize_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите ваш Binance API ключ и секрет через пробел:")
    await state.set_state(FormState.waiting_for_api_keys)

@router.message(FormState.waiting_for_api_keys)
async def handle_binance_api_keys(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    keys = message.text.split()

    if len(keys) != 2:
        await message.answer("❌ Неверный формат! Введите API-ключ и секрет через пробел.")
        return
    
    api_key, api_secret = keys

    try:
        client = Client(api_key, api_secret)
        client.get_account()

        save_api_keys(user_id, api_key, api_secret)  # ✅ Сохраняем ключи в БД

        await message.answer("✅ Авторизация успешна! Теперь у вас есть постоянное меню.", reply_markup=kb.persistent_menu_keyboard)
        await state.clear()
    except Exception as e:
        await message.answer("❌ Ошибка авторизации. Проверьте ключи.")

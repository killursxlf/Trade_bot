from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.balance_handler import balance_reply
from handlers.currency_handler import currency_pair_reply
import keyboards.keyboards as kb

router = Router()

@router.message(Command("menu"))
async def show_inline_menu(message: types.Message):
    await message.reply("📌 Главное меню:", reply_markup=kb.main_menu_keyboard)

@router.message(lambda message: message.text == "📊 Просмотр баланса")
async def balance_button_handler(message: types.Message):
    await balance_reply(message)  

@router.message(lambda message: message.text == "💱 Просмотр валютной пары")
async def currency_button_handler(message: types.Message, state: FSMContext):
    await currency_pair_reply(message, state)  

@router.message(lambda message: message.text == "❌ Выход")
async def exit_button_handler(message: types.Message):
    await message.reply("👋 Вы вышли из меню.", reply_markup=types.ReplyKeyboardRemove())

@router.callback_query(F.data == "view_balance")
async def inline_balance_handler(call: types.CallbackQuery):
    await balance_reply(call.message)  

@router.callback_query(F.data == "view_currency_pair")
async def inline_currency_handler(call: types.CallbackQuery, state: FSMContext):
    await currency_pair_reply(call.message, state)  
    
@router.callback_query(F.data == "exit_menu")
async def inline_exit_handler(call: types.CallbackQuery):
    await call.message.answer("👋 Вы вышли из меню.", reply_markup=types.ReplyKeyboardRemove())

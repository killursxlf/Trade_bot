import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers.auth_handler import router as auth_router
from handlers.balance_handler import router as balance_router  
from handlers.currency_handler import router as currency_router
from handlers.menu_handler import router as menu_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(auth_router)
dp.include_router(balance_router)  
dp.include_router(currency_router)
dp.include_router(menu_router)

async def main():
    logging.info("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен 🛑")

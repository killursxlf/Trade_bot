import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from services.database import create_tables 
from handlers.auth_handler import router as auth_router
from handlers.balance_handler import router as balance_router
from handlers.currency_handler import router as currency_router
from handlers.menu_handler import router as menu_router
from handlers.alerts_handler import router as alert_router
from handlers.top_handler import router as top_router
from handlers.favorites_handler import router as favorites_router
from handlers.volume_handler import router as volume_router
from handlers.hot_handler import router as hot_router
from services.alerts_checker import check_alerts

create_tables()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

routers = [
    auth_router, balance_router, currency_router, menu_router, 
    alert_router, favorites_router, top_router, hot_router, volume_router
]

for router in routers:
    dp.include_router(router)


async def main():
    logging.info("Бот запущен 🚀")

    loop = asyncio.get_event_loop()
    loop.create_task(check_alerts(bot))

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен 🛑")

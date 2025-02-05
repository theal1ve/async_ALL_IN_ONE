from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.config import settings
import asyncio
import os


async def main():
    bot = Bot(settings.TG_KEY)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Start")
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

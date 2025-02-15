from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.config import settings
from app.middleware import BlockCheckMiddleware
import asyncio


async def main():
    bot = Bot(settings.TG_KEY)
    dp = Dispatcher()
    dp.update.middleware(BlockCheckMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Start")
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

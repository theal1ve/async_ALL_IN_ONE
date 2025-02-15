from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.exceptions import TelegramForbiddenError
from typing import Callable, Awaitable, Any
from app.database.queries.orm import update_user

class BlockCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        bot = data["bot"]
        user_id = event.from_user.id

        try:
            await bot.get_chat(user_id)
            return await handler(event, data)  
        except TelegramForbiddenError:
            print(f"Пользователь {user_id} заблокировал бота.")
            await update_user(id=user_id, dict_wtih_values={"alive": 0})
            return  
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from app.database.queries.orm import update_user
from aiogram.types import Update


class BlockCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        try:
            return await handler(event, data)
        except TelegramAPIError as e:
            if "bot was blocked by the user" in str(e).lower():
                user_id = event.message.from_user.id
                await update_user(id=user_id, dict_wtih_values={"alive": 0})



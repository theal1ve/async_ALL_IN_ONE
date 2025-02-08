from app.database.queries.orm import checking_for_admin
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand)
from aiogram.utils.keyboard import InlineKeyboardBuilder


"""BACK_MAIN_MENU = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Главное меню", callback_data="main_menu")]])"""


async def create_help_kb(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='/main_menu', callback_data='help_main_menu'),
                InlineKeyboardButton(text='/chat', callback_data='help_chat'))
    builder.adjust(2, 1)

    if await checking_for_admin(id):
        builder.add(InlineKeyboardButton(text='/mailing', callback_data='help_mailing'),
                    InlineKeyboardButton(
                        text='/add_admin', callback_data='help_add_admin'),
                    InlineKeyboardButton(
                        text='/delete_admin', callback_data='help_delete_admin'),
                    InlineKeyboardButton(text='/get_users', callback_data='help_count_of_users'))
        builder.adjust(3, 3)

    # builder.row(BACK_MAIN_MENU.inline_keyboard[0][0])

    return builder.as_markup()


async def create_commands_menu(id: int) -> list:
    Commands = [BotCommand(command="start", description="Запуск/перезапуск бота🔄"),
                BotCommand(command="chat", description="Написать Chat-GPT💬"),
                BotCommand(command="picture",
                           description="Сгенерировать картинку🌄"),
                BotCommand(command="help", description="Обьяснить подробнее про каждую кнопку😵‍💫")]
    if await checking_for_admin(id):
        Commands = Commands + [BotCommand(command="get_users", description="выводит кол-во пользователей👥"),
                               BotCommand(command="add_admin",
                                          description="Добавляет админа➕"),
                               BotCommand(command="delete_admin",
                                          description="Удаляет админа➖"),
                               BotCommand(command="mailing", description="Рассылка📬")]
    return Commands

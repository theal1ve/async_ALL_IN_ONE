from app.database.queries.orm import checking_for_admin, checking_for_model_for_chat_or_image, checking_for_promt_for_chat
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, BotCommandScopeChat)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.const import promt_for_check_news, promt_for_programmer_or_IT

get_unlimit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text="ПОЛУЧИТЬ БЕЗЛИМИТ", callback_data="get_unlimit")]])


async def create_help_kb(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='/chat', callback_data='help_chat'),
                InlineKeyboardButton(text="/image", callback_data="help_picture"))
    builder.adjust(2, 1)

    if await checking_for_admin(id):
        builder.add(InlineKeyboardButton(text='/add_admin', callback_data='help_add_admin'),
                    InlineKeyboardButton(
                        text='/delete_admin', callback_data='help_delete_admin'),
                    InlineKeyboardButton(
                        text='/add_channel', callback_data='help_add_channel'),
                    InlineKeyboardButton(
                        text='/delete_channel', callback_data='help_delete_channel'),
                    InlineKeyboardButton(
                        text='/add_unlimit', callback_data='help_add_unlimit'),
                    InlineKeyboardButton(
                        text='/delete_unlimit', callback_data='help_delete_unlimit'),
                    InlineKeyboardButton(
                        text='/get_users', callback_data='help_get_users'),
                    InlineKeyboardButton(
                        text='/mailing', callback_data='help_mailing')

                    )
        builder.adjust(3, 3)

    return builder.as_markup()


async def create_commands_menu(id: int, bot) -> None:
    Commands = [BotCommand(command="start", description="Запуск/перезапуск бота🔄"),
                BotCommand(command="chat", description="Задать вопрос💬"),
                BotCommand(command="image",
                           description="Сгенерировать картинку🌄"),
                BotCommand(command="help", description="Обьяснить подробнее про каждую кнопку😵‍💫")]
    if await checking_for_admin(id):
        Commands = Commands + [BotCommand(command="add_admin", description="Добавляет админа➕"),
                               BotCommand(command="delete_admin",
                                          description="Удаляет админа➖"),
                               BotCommand(
                                   command="add_channel", description="Добавить канал для подписки➕"),
                               BotCommand(
                                   command="delete_channel", description="Удалить канал для подписки➖"),
                               BotCommand(
                                   command="add_unlimit", description="Добавить \"безлимит\" пользователю➕"),
                               BotCommand(
                                   command="delete_unlimit", description="Удалить \"безлимит\" пользователю➖"),
                               BotCommand(
                                   command="get_users", description="выводит кол-во пользователей👥"),
                               BotCommand(command="mailing", description="Рассылка📬")]

    await bot.set_my_commands(commands=Commands, scope=BotCommandScopeChat(chat_id=id))


async def create_channels_kb(CHANNELS_URL: list) -> InlineKeyboardMarkup:
    if CHANNELS_URL:
        builder = InlineKeyboardBuilder()
        cnt = 0
        for url in CHANNELS_URL:
            cnt += 1
            builder.add(InlineKeyboardButton(text=f"Канал {cnt}", url=url))
        builder.adjust(3, -(-cnt // 3))
        builder.row(InlineKeyboardButton(
            text="Готово!", callback_data="sub_done"))
        return builder.as_markup()


async def create_promt_kb(id: int):
    builder = InlineKeyboardBuilder()
    active = await checking_for_promt_for_chat(id=id)
    if active == promt_for_programmer_or_IT:
        builder.add(InlineKeyboardButton(text="IT/Coding✅", callback_data="promt_in_depth_study_of_it_or_coding"),
                    InlineKeyboardButton(text="Check news", callback_data="promt_checking_news"),
                    InlineKeyboardButton(text="Обычный", callback_data="promt_usual"))
    elif active == promt_for_check_news:
        builder.add(InlineKeyboardButton(text="IT/Coding", callback_data="promt_in_depth_study_of_it_or_coding"),
                    InlineKeyboardButton(
                        text="Check news✅", callback_data="promt_checking_news"),
                    InlineKeyboardButton(text="Обычный", callback_data="promt_usual"))
    elif active == "":
        builder.add(InlineKeyboardButton(text="IT/Coding", callback_data="promt_in_depth_study_of_it_or_coding"),
                    InlineKeyboardButton(
                        text="Check news", callback_data="promt_checking_news"),
                    InlineKeyboardButton(text="Обычный✅", callback_data="promt_usual"))
    builder.add(InlineKeyboardButton(text="Далее", callback_data="continue"))

    builder.adjust(2, 1)

    return builder.as_markup()


async def create_chat_kb(id: int):
    builder = InlineKeyboardBuilder()
    active = await checking_for_model_for_chat_or_image(id=id, for_chat_or_image="chat")
    if active == "deepseek-v3":
        builder.add(InlineKeyboardButton(text="deepseek-v3✅", callback_data="on_deepseek-v3"),
                    InlineKeyboardButton(
                        text="deepseek-r1", callback_data="on_deepseek-r1"),
                    InlineKeyboardButton(text="ChatGPT-4", callback_data="on_gpt-4"))
    elif active == "deepseek-r1":
        builder.add(InlineKeyboardButton(text="deepseek-v3", callback_data="on_deepseek-v3"),
                    InlineKeyboardButton(
                        text="deepseek-r1✅", callback_data="on_deepseek-r1"),
                    InlineKeyboardButton(text="ChatGPT-4", callback_data="on_gpt-4"))
    elif active == "gpt-4":
        builder.add(InlineKeyboardButton(text="deepseek-v3", callback_data="on_deepseek-v3"),
                    InlineKeyboardButton(
                        text="deepseek-v1", callback_data="on_deepseek-r1"),
                    InlineKeyboardButton(text="ChatGPT-4✅", callback_data="on_gpt-4"))

    builder.adjust(2, 2)

    return builder.as_markup()


async def create_image_kb(id: int):
    active = await checking_for_model_for_chat_or_image(id=id, for_chat_or_image="image")
    builder = InlineKeyboardBuilder()
    if active == "midjourney":
        builder.add(InlineKeyboardButton(text="flux", callback_data="on_flux"),
                    InlineKeyboardButton(text="midjourney✅", callback_data="on_midjourney"))
    elif active == "flux":
        builder.add(InlineKeyboardButton(text="flux✅", callback_data="on_flux"),
                    InlineKeyboardButton(text="midjourney", callback_data="on_midjourney"))

    builder.adjust(2, 1)

    return builder.as_markup()

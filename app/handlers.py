from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import CommandStart, Command
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED, LEAVE_TRANSITION
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.queries.orm import *
from app.const import *
from app.keyboard import *
from app.chat_gpt import *
import asyncio

router = Router()


class For_got_data(StatesGroup):
    message_for_mailing = State()
    message_for_gpt = State()
    id_for_delete_or_add_admin = State()
    message_for_picture = State()
    id_for_delete_or_add_unlimit = State()


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_blocked_by_user(event: ChatMemberUpdated, bot: Bot) -> None:
    if event.chat.type == "private" and event.new_chat_member.user.id == bot.id:
        if event.new_chat_member == "kicked":
            await update_user(event.from_user.id, {"alive": 0})
        elif event.old_chat_member == "kicked":
            await update_user(event.from_user.id, {"alive": 1})
            await bot.send_message(event.from_user.id, "Очень рады, что вы вернулись!")


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    await create_tables()
    await create_user(id=message.from_user.id)
    await bot.set_my_commands(await create_commands_menu(id=message.from_user.id))
    if await checking_for_admin(message.from_user.id):
        await message.answer(answer_to_cmd_start_for_admin.format(message.from_user.first_name), parse_mode="html")
    else:
        await message.answer(answer_to_cmd_start_for_people.format(message.from_user.first_name), parse_mode="html")


@router.message(Command("add_unlimit"))
async def cmd_add_unlimit(message: Message, state: FSMContext) -> None:
    await message.answer("Напишите id пользователя, которому дать \"безлимит\"")
    await state.set_data({"unlimit": 1})
    await state.set_state(For_got_data.id_for_delete_or_add_unlimit)


@router.message(Command("delete_unlimit"))
async def cmd_add_unlimit(message: Message, state: FSMContext) -> None:
    await message.answer("Напишите id пользователя, которому удалить \"безлимит\"")
    await state.set_data({"unlimit": 0})
    await state.set_state(For_got_data.id_for_delete_or_add_unlimit)


@router.message(Command("picture"))
async def cmd_picture(message: Message, state: FSMContext) -> None:
    id: int = message.from_user.id

    count_generate: int = await cheking_for_count_generate(id=id)

    if await checking_for_unlimit(id=id) or count_generate != 5 or \
            type(await get_datetime_of_first_generate(id=id)) == bool:

        if count_generate == 0:
            await update_user(id=id, dict_wtih_values={"datetime_of_first_generate": datetime.now()})

        await message.answer("Напишите, какую картинку вас сгенерировать")
        await state.set_state(For_got_data.message_for_picture)

    else:
        datetime_refresh: timedelta = await get_datetime_of_first_generate(id=id) - datetime.now()
        await message.answer(f"У вас закончились запросы. Запросы обновятся через {datetime_refresh.seconds // 3600}ч {(datetime_refresh.seconds % 3600) // 60}мин")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("<b>Нажмите на кнопку, которая вам не понятна.</b>", parse_mode="html", reply_markup=await create_help_kb(message.from_user.id))


@router.message(Command("chat"))
async def cmd_chat(message: Message, state: FSMContext) -> None:
    await message.answer("Напишите сообщение свой вопрос")
    await state.set_state(For_got_data.message_for_gpt)
    await state.set_data({"history": []})


@router.message(Command("get_users"))
async def cmd_get_users(message: Message) -> None:
    if await checking_for_admin(message.from_user.id):
        alive_users, all_users = await select_users()
        alive_users = len(alive_users)
        all_users = len(all_users)
        await message.answer(for_CMD_get_users.format(all_users, alive_users, (all_users-all_users)), parse_mode="html")


@router.message(Command("mailing"))
async def cmd_mailing(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await message.answer("Напишите сообщение для рассылки")
        await state.set_state(For_got_data.message_for_mailing)


@router.message(Command("add_admin"))
async def cmd_add_admin(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await state.set_data({"admin": 1})
        await state.set_state(For_got_data.id_for_delete_or_add_admin)
        await message.answer("Пришлите <b>id</b> пользователя, которого вы хотите сделать админом", parse_mode="html")


@router.message(Command("delete_admin"))
async def cmd_delete_admin(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await state.set_data({"admin": 0})
        await message.answer("Пришлите <b>id</b> админа, которого вы хотите сделать обычным пользователем", parse_mode="html")


@router.message(For_got_data.message_for_mailing)
async def do_mailing(message: Message, state: FSMContext, bot: Bot) -> None:
    state_message = message.text
    if await checking_for_admin(message.from_user.id):
        alive_users = (await select_users())[0]
        for user_id in alive_users:
            await bot.send_message(chat_id=user_id[0], text=state_message)
        await state.clear()


@router.message(For_got_data.id_for_delete_or_add_unlimit)
async def delete_or_add_unlimit(message: Message, state: FSMContext) -> None:
    unlimit: int = (await state.get_data())["unlimit"]
    id: int = message.from_user.id
    await update_user(id=id, dict_wtih_values={"unlimit": unlimit})
    await message.answer("\"Безлимит\" выдан!") if unlimit == 1 else await message.answer("\"Безлимит\" удален!")


@router.message(For_got_data.id_for_delete_or_add_admin)
async def delete_or_add_admin(message: Message, state: FSMContext) -> None:
    admin = (await state.get_data())["admin"]
    await update_user(id=int(message.text), dict_wtih_values={"unlimit": admin, "admin": admin})
    await message.answer("Админ добавлен!") if admin == 1 else await message.answer("Админ удален!")


@router.message(For_got_data.message_for_gpt)
async def create_answer_by_gpt(message: Message, state: FSMContext, bot: Bot) -> None:
    history = (await state.get_data())["history"]
    state_message = message.text
    await bot.send_chat_action(message.from_user.id, action="typing")
    sent_message = await message.answer("Генерирую ответ...")
    history.append({"role": "user", "content": state_message})
    answer, history = await create_response(history)
    await sent_message.edit_text(answer)
    await state.clear()
    await state.set_state(For_got_data.message_for_gpt)
    await state.update_data({"history": history})


@router.message(For_got_data.message_for_picture)
async def create_picture(message: Message, bot: Bot, state: FSMContext) -> None:
    id: int = message.from_user.id
    sent_message = await message.answer("Генерирую ответ...")
    url = await generate_image(message.text)
    await bot.send_photo(chat_id=message.from_user.id, caption="Готово!", photo=url)
    await state.clear()
    await update_user(id=id, dict_wtih_values={"count_generate": 0})
    await state.set_state(For_got_data.message_for_picture)

"""
@router.callback_query(F.data == "main_menu")
async def answer_to_main_menu(callback: CallbackQuery, bot: Bot) -> None:
    if await checking_for_admin(callback.from_user.id):
        await callback.message.edit_text(main_menu_for_admin)
    else:
        await callback.message.edit_text(main_menu_for_people)"""


@router.callback_query(F.data == "help_chat")
async def answer_to_help_chat(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите боту сообщение, которое вы бы хотели отправить ChatGPT-4.', show_alert=True)


@router.callback_query(F.data == "help_main_menu")
async def answer_to_help_main_menu(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, бот вернет вас в меню команд.', show_alert=True)


@router.callback_query(F.data == "help_add_admin")
async def answer_to_add_admin(callback: CallbackQuery) -> None:
    if await checking_for_admin(callback.from_user.id):
        await callback.answer('После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который станет админом.', show_alert=True)


@router.callback_query(F.data == "help_delete_admin")
async def answer_to_delete_admin(callback: CallbackQuery) -> None:
    if await checking_for_admin(callback.from_user.id):
        await callback.answer('После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который будет удален из админов.', show_alert=True)


@router.callback_query(F.data == "help_count_of_users")
async def answer_to_count_of_users(callback: CallbackQuery) -> None:
    if await checking_for_admin(callback.from_user.id):
        await callback.answer('После того, как нажмете на эту кнопку, бот выведет количество пользователей этого бота.', show_alert=True)


@router.callback_query(F.data == "help_mailing")
async def answer_to_mailing(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите сообщение, котрое будет разослано всем польхователям этого бота.', show_alert=True)

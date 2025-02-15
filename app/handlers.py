from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import CommandStart, Command
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, LEAVE_TRANSITION, CREATOR
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.queries.orm import *
from app.const import *
from app.keyboards import *
from app.create_chat_and_image import *


router = Router()


CHANNELS_ID = [-1002013250812]
CHANNELS_URL = ["https://t.me/thealivelive"]


async def is_subscribed(user_id: int, bot: Bot, message_id: int = False) -> None:
    for id in CHANNELS_ID:
        member = await bot.get_chat_member(chat_id=id, user_id=user_id)
        if member.status in ["member", "administrator", "creator"] or await checking_for_unlimit(id=user_id) == 2 or await checking_for_admin(id=user_id):
            if message_id:
                await bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Спасибо за подписки! \"Безлимит\" активирован", reply_markup=None)
            await update_user(id=user_id, dict_wtih_values={"unlimit": 1})
        else:
            await update_user(id=user_id, dict_wtih_values={"unlimit": 0})
            if message_id:
                await bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Подпишитесь на все каналы!")
                await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=await create_channels_kb(CHANNELS_URL))
            return None


class For_got_data(StatesGroup):
    message_for_mailing = State()
    for_get_promt = State()
    message_for_gpt = State()
    id_for_delete_or_add_admin = State()
    message_for_image = State()
    id_for_delete_or_add_unlimit = State()
    channels_id_for_subs = State()
    channels_url_for_subs = State()


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed="leave_transition"))
async def bot_blocked_by_user(event: ChatMemberUpdated, bot: Bot) -> None:
    if event.chat.type == "private" and event.new_chat_member.user.id == bot.id:
        if event.new_chat_member == "kicked":
            await update_user(event.from_user.id, {"alive": 0})
        elif event.old_chat_member == "kicked":
            await update_user(event.from_user.id, {"alive": 1})
            await bot.send_message(event.from_user.id, "Очень рады, что вы вернулись!")

# ----------------------------------------------------------------------------------------------------------------------------------------------------------


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    await create_user(id=message.from_user.id)
    await create_commands_menu(id=message.from_user.id, bot=bot)
    if await checking_for_admin(message.from_user.id):
        await message.answer(answer_to_cmd_start_for_admin.format(message.from_user.first_name), parse_mode="html")
    else:
        await message.answer(answer_to_cmd_start_for_people.format(message.from_user.first_name), parse_mode="html")


@router.message(Command("add_channel"))
async def cmd_set_channels(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await message.answer("Напишите id канала")
        await state.set_data({"delete": 0})
        await state.set_state(For_got_data.channels_id_for_subs)


@router.message(Command("delete_channel"))
async def cmd_set_channels(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await message.answer("Напишите id канала")
        await state.set_data({"delete": 1})
        await state.set_state(For_got_data.channels_id_for_subs)


@router.message(Command("add_unlimit"))
async def cmd_add_unlimit(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await message.answer("Напишите id пользователя, которому дать \"безлимит\"")
        await state.set_data({"unlimit": 2})
        await state.set_state(For_got_data.id_for_delete_or_add_unlimit)


@router.message(Command("delete_unlimit"))
async def cmd_add_unlimit(message: Message, state: FSMContext) -> None:
    if await checking_for_admin(message.from_user.id):
        await message.answer("Напишите id пользователя, которому удалить \"безлимит\"")
        await state.set_data({"unlimit": 0})
        await state.set_state(For_got_data.id_for_delete_or_add_unlimit)


@router.message(Command("image"))
async def cmd_image(message: Message, state: FSMContext, bot: Bot) -> None:
    id: int = message.from_user.id
    await is_subscribed(user_id=id, bot=bot)
    count_generate: int = await checking_for_count_generate(id=id)
    if count_generate != 5 or type(await get_datetime_of_first_generate(id=id)) == bool or \
            await checking_for_unlimit(id=id):
        if count_generate == 0:
            await update_user(id=id, dict_wtih_values={"datetime_of_first_generate": datetime.now()})
        await message.answer("Напишите, какую картинку вам сгенерировать", reply_markup=await create_image_kb(id))
        await state.set_state(For_got_data.message_for_image)
    else:
        datetime_refresh: timedelta = await get_datetime_of_first_generate(id=id) - datetime.now()
        await message.answer(f"У вас закончились запросы. Запросы обновятся через {datetime_refresh.seconds // 3600}ч {(datetime_refresh.seconds % 3600) // 60}мин", reply_markup=get_unlimit)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("<b>Нажмите на кнопку, которая вам не понятна.</b>", parse_mode="html", reply_markup=await create_help_kb(message.from_user.id))


@router.message(Command("chat"))
async def cmd_chat(message: Message) -> None:
    id: int = message.from_user.id
    await message.answer("Выберите специализацию ИИ", reply_markup=await create_promt_kb(id=id))


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
        await state.set_state(For_got_data.id_for_delete_or_add_admin)

# --------------------------------------------------------------------------------------------------------------------------------------------


@router.message(For_got_data.message_for_mailing)
async def do_mailing(message: Message, state: FSMContext, bot: Bot) -> None:
    state_message = message.text
    if await checking_for_admin(message.from_user.id):
        alive_users = (await select_users())[0]
        for user_id in alive_users:
            await bot.send_message(chat_id=user_id[0], text=state_message)
        await state.clear()


@router.message(For_got_data.id_for_delete_or_add_admin)
async def delete_or_add_admin(message: Message, state: FSMContext) -> None:
    admin = (await state.get_data())["admin"]
    await update_user(id=int(message.text), dict_wtih_values={"unlimit": admin, "admin": admin})
    await message.answer("Админ добавлен!") if admin == 1 else await message.answer("Админ удален!")


@router.message(For_got_data.id_for_delete_or_add_unlimit)
async def delete_or_add_unlimit(message: Message, state: FSMContext) -> None:
    unlimit: int = (await state.get_data())["unlimit"]
    id: int = int(message.text)
    await update_user(id=id, dict_wtih_values={"unlimit": unlimit})
    await message.answer("\"Безлимит\" выдан!") if unlimit == 2 else await message.answer("\"Безлимит\" удален!")


@router.message(For_got_data.message_for_gpt)
async def create_answer_by_gpt(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        history = (await state.get_data())["history"]
        state_message = message.text
        model = await checking_for_model_for_chat_or_image(id=message.chat.id, for_chat_or_image="chat")
        await bot.send_chat_action(message.from_user.id, action="typing")
        sent_message = await message.answer("Генерирую ответ...💬")
        history.append({"role": "user", "content": state_message})
        answer, history = await create_response(history, model)
        await sent_message.edit_text(answer, parse_mode="Markdown")
        await state.clear()
        await state.set_state(For_got_data.message_for_gpt)
        await state.update_data({"history": history})
    except TelegramBadRequest:
        pass


@router.message(For_got_data.message_for_image)
async def create_picture(message: Message, bot: Bot, state: FSMContext, message_bad_request=False) -> None:
    try:
        id: int = message.from_user.id
        count_generate: int = await checking_for_count_generate(id=id)
        model = await checking_for_model_for_chat_or_image(id=id, for_chat_or_image="image")
        if count_generate != 5 or await checking_for_unlimit(id=id):
            if message_bad_request:
                url = await generate_image(message.text, model=model)
                await bot.send_photo(chat_id=message.from_user.id, caption="Готово!", photo=url)
            else:
                await message.answer("Генерирую фото...💬")
                url = await generate_image(message.text, model)
                await bot.send_photo(chat_id=message.from_user.id, caption="Готово!", photo=url)
            await state.clear()
            await update_user(id=id, dict_wtih_values={"count_generate": 0})
            await state.set_state(For_got_data.message_for_image)
        else:
            datetime_refresh: timedelta = await get_datetime_of_first_generate(id=id) - datetime.now()
            await message.answer(f"У вас закончились запросы. Запросы обновятся через {datetime_refresh.seconds // 3600}ч {(datetime_refresh.seconds % 3600) // 60}мин", reply_markup=get_unlimit)
    except TelegramBadRequest:
        await create_picture(message=message, bot=bot, state=state, message_bad_request=True)


@router.message(For_got_data.channels_id_for_subs)
async def change_channels_id_for_subs(message: Message, state: FSMContext) -> None:
    id: int = message.text
    if (await state.get_data())["delete"]:
        del CHANNELS_ID[CHANNELS_ID.index(id)]
    else:
        CHANNELS_ID.append(id)
    await message.answer(f"Напишите URL канала")
    await state.set_state(For_got_data.channels_url_for_subs)


@router.message(For_got_data.channels_url_for_subs)
async def change_channels_id_for_subs(message: Message, state: FSMContext) -> None:
    url: str = message.text
    if (await state.get_data())["delete"]:
        del CHANNELS_URL[CHANNELS_URL.index(url)]
    else:
        CHANNELS_URL.append(url)
    await message.answer(f"Успешно!")
    await state.clear()

# -------------------------------------------------------------------------------------------------------------------------------------------------------


@router.callback_query(F.data == "help_chat")
async def answer_to_help_chat(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите боту сообщение, которое вы бы хотели отправить ChatGPT.', show_alert=True)


@router.callback_query(F.data == "help_picture")
async def answer_to_help_chat(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите боту сообщение, которое описывает желанную вами картинку.', show_alert=True)


@router.callback_query(F.data == "help_add_admin")
async def answer_to_add_admin(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который станет админом.', show_alert=True)


@router.callback_query(F.data == "help_delete_admin")
async def answer_to_delete_admin(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который будет удален из админов.', show_alert=True)


@router.callback_query(F.data == "help_add_channel")
async def answer_to_add_channel(callback: CallbackQuery) -> None:
    await callback.answer(for_answer_to_add_chennel, show_alert=True)


@router.callback_query(F.data == "help_delete_channel")
async def answer_to_delete_channel(callback: CallbackQuery) -> None:
    await callback.answer(for_answer_to_delete_chennel, show_alert=True)


@router.callback_query(F.data == "help_add_unlimit")
async def answer_to_add_unlimit(callback: CallbackQuery) -> None:
    await callback.answer("После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который получит \"безлимит\" на генерации картинок.", show_alert=True)


@router.callback_query(F.data == "help_delete_unlimit")
async def answer_to_add_unlimit(callback: CallbackQuery) -> None:
    await callback.answer("После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который будет без \"безлимита\" на генерации картинок.", show_alert=True)


@router.callback_query(F.data == "help_get_users")
async def answer_to_count_of_users(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, бот выведет количество пользователей этого бота.', show_alert=True)


@router.callback_query(F.data == "help_mailing")
async def answer_to_mailing(callback: CallbackQuery) -> None:
    await callback.answer('После того, как нажмете на эту кнопку, напишите сообщение, котрое будет разослано всем польхователям этого бота.', show_alert=True)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------


@router.callback_query(F.data == "promt_in_depth_study_of_it_or_coding")
async def choose_promt_for_programmer_or_IT(callback: CallbackQuery) -> None:
    id = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"promt_for_chat": promt_for_programmer_or_IT})
    await callback.message.edit_reply_markup(reply_markup=await create_promt_kb(id))
    await callback.answer()


@router.callback_query(F.data == "promt_checking_news")
async def choose_promt_for_checking_news(callback: CallbackQuery) -> None:
    id = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"promt_for_chat": promt_for_check_news})
    await callback.message.edit_reply_markup(reply_markup=await create_promt_kb(id))
    await callback.answer()


@router.callback_query(F.data == "promt_usual")
async def choose_promt_for_usual(callback: CallbackQuery) -> None:
    id = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"promt_for_chat": ""})
    await callback.message.edit_reply_markup(reply_markup=await create_promt_kb(id))
    await callback.answer()


@router.callback_query(F.data == "on_deepseek-v3")
async def choose_deepseek_v3(callback: CallbackQuery) -> None:
    id = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"model_for_chat": "deepseek-v3"})
    await callback.message.edit_reply_markup(reply_markup=await create_chat_kb(id))
    await callback.answer()


@router.callback_query(F.data == "on_deepseek-r1")
async def choose_deepseek_r1(callback: CallbackQuery) -> None:
    id: int = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"model_for_chat": "deepseek-r1"})
    await callback.message.edit_reply_markup(reply_markup=await create_chat_kb(id))
    await callback.answer()


@router.callback_query(F.data == "on_gpt-4")
async def choose_gpt_4(callback: CallbackQuery) -> None:
    id: int = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"model_for_chat": "gpt-4"})
    await callback.message.edit_reply_markup(reply_markup=await create_chat_kb(id))
    await callback.answer()


@router.callback_query(F.data == "on_flux")
async def choose_flux(callback: CallbackQuery) -> None:
    id: int = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"model_for_image": "flux"})
    await callback.message.edit_reply_markup(reply_markup=await create_image_kb(id))
    await callback.answer()


@router.callback_query(F.data == "on_midjourney")
async def choose_midjourney(callback: CallbackQuery) -> None:
    id: int = callback.from_user.id
    await update_user(id=id, dict_wtih_values={"model_for_image": "midjourney"})
    await callback.message.edit_reply_markup(reply_markup=await create_image_kb(id))
    await callback.answer()

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


@router.callback_query(F.data == "get_unlimit")
async def getting_unlimit(callback: CallbackQuery, bot: Bot) -> None:
    if CHANNELS_URL:
        await callback.message.edit_text(text="Для получения \"безлимита\" подпишитесь на эти каналы", reply_markup=await create_channels_kb(CHANNELS_URL))
    else:
        await callback.message.edit_text("Таких каналов пока нет...")


@router.callback_query(F.data == "sub_done")
async def is_subscribed_with_message_id(callback: CallbackQuery, bot: Bot) -> None:
    await is_subscribed(user_id=callback.from_user.id, bot=bot, message_id=callback.message.message_id)


@router.callback_query(F.data == "continue")
async def next_kb(callback: CallbackQuery, state: FSMContext) -> None:
    id: int = callback.from_user.id
    promt = await checking_for_promt_for_chat(id=id)
    await callback.message.edit_text(text="Выберите модель и напишите ваш вопрос", reply_markup=await create_chat_kb(id=id))
    await state.set_state(For_got_data.message_for_gpt)
    await state.set_data({"history": [{"role": "user", "content": promt}]})

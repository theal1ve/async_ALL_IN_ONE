from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text, update, values
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload
from datetime import datetime, timedelta
from app.database.database import Base, async_engine, async_session_factory
from app.database.models import Users


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_user(id: int, alive: int = 1, unlimit: int = 0, admin: int = 0, 
                      count_of_generate: int = 0) -> None:
    async with async_session_factory() as session:
        query = (select(Users.id).filter_by(id=id).exists())
        check_user = await session.scalar(select(query))
        if not check_user:
            user = Users(id=id, alive=alive, unlimit=unlimit, admin=admin, count_generate=count_of_generate)
            session.add(user)
            await session.flush()
            await session.commit()


async def update_user(id: int, dict_wtih_values: dict) -> None:
    async with async_session_factory() as session:
        query = update(Users).where(Users.id == id).values(**dict_wtih_values)
        if not (await checking_for_unlimit(id=id)):
            if "count_generate" in dict_wtih_values.keys():
                query = update(Users).where(Users.id == id).values(count_generate=Users.count_generate + dict_wtih_values["count_generate"] + 1)
        await session.execute(query)
        await session.flush()
        await session.commit()


async def checking_for_admin(id: int) -> int:
    async with async_session_factory() as session:
        query = select(Users.admin).where(Users.id == id)
        admin = (await session.execute(query)).one()[0]
        return admin


async def select_users() -> int:
    async with async_session_factory() as session:
        query_1 = select(Users.id).where(Users.alive == 1)
        alive_users = (await session.execute(query_1)).all()
        query_2 = select(Users.id)
        all_users = (await session.execute(query_2)).all()
        return alive_users, all_users


async def checking_for_unlimit(id: int) -> int:
    async with async_session_factory() as session:
        query = select(Users.unlimit).where(Users.id == id)
        unlimit = (await session.execute(query)).one()[0]
        return unlimit


async def cheking_for_count_generate(id: int) -> int:
    async with async_session_factory() as session:
        query = select(Users.count_generate,
                       Users.datetime_of_first_generate).where(Users.id == id)
        count_generate = (await session.execute(query)).one()[0]
        return count_generate


async def get_datetime_of_first_generate(id: int):
    async with async_session_factory() as session:
        query = select(Users.datetime_of_first_generate).where(Users.id == id)
        get_datetime_of_first_generate: datetime = (await session.execute(query)).one()[0] + timedelta(days=1)
        if get_datetime_of_first_generate - datetime.now() <= timedelta(seconds=0):
            await update_user(id=id, dict_wtih_values={"count_generate": -6})
            get_datetime_of_first_generate = True
        return get_datetime_of_first_generate

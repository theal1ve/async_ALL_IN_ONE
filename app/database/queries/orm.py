from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text, update, values
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload

from app.database.database import Base, async_engine, async_session_factory
from app.database.models import Users


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def insert_user(id, alive=0, unlimit_questions=0, admin=0):
    async with async_session_factory() as session:
        query = (select(Users.id).filter_by(id=id).exists())
        check_user = await session.scalar(select(query))
        if not check_user:
            user = Users(id=id, alive=alive, unlimit_questions=unlimit_questions, admin=admin)
        else:
            user = update(Users).where(Users.c.id == id).values(alive=alive)
        session.add(user)
        await session.flush()
        await session.commit()


async def checking_for_admin(id):
    async with async_session_factory () as session:
        query = select(Users.admin).where(Users.id == id)
        admin = await session.execute(query)
        return admin


async def select_users():
    async with async_session_factory() as session:
        query_1 = select(Users.id).where(Users.alive == 1)
        alive_users = (await session.execute(query_1)).all()
        query_2 = select(Users.id)
        all_users = (await session.execute(query_2)).all()
        return alive_users, all_users
    

async def user_alive_or_death(alive: int, id: int):
    async with async_session_factory() as session:
        query = (update(Users)
                 .where(Users.id==id)
                 .values(alive=alive))
        await session.execute(query)
        await session.commit()
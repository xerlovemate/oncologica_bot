from database.db import async_session
from database.db import User
from sqlalchemy import select
from aiogram import Bot
from config import TOKEN

bot = Bot(token=TOKEN)


async def set_user(tg_id: int, username: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.tg_username = username
            else:
                user = User(
                    tg_id=tg_id,
                    tg_username=username,
                )
                session.add(user)

            await session.commit()


async def set_user_phone_and_name(tg_id: int, user_name: str, phone_number: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.user_name = user_name
                user.phone_number = phone_number

            await session.commit()


async def get_user_name_by_tg_id(tg_id: int) -> str | None:
    async with async_session() as session:
        result = await session.execute(
            select(User.user_name).where(User.tg_id == tg_id)
        )
        user_name = result.scalar_one_or_none()

        return user_name

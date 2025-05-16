import asyncio
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import TOKEN
from database.db import async_main
from handlers import (
    start
)


async def main():
    # Создаем базу данных и таблицы
    await async_main()  # Создание всех таблиц перед запуском бота

    # Создание асинхронного движка и сессии
    engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # Инициализация бота
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_routers(
        start.router,
    )

    # Запуск процесса polling для бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from .config import conn_url

Base = declarative_base()


engine = create_async_engine(conn_url, echo=False)


async_session = async_sessionmaker(expire_on_commit=False, autoflush=False, class_=AsyncSession, bind=engine)


async def init_db():
    """Создание таблиц."""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # для теста дропаем таблицы, что бы не бороться с конфликтами
        await conn.run_sync(Base.metadata.create_all)


import datetime
from sqlalchemy import select, update
from .. database import async_session
from .. models import User


async def add_user(user_id: int, text: str = None):
    async with async_session() as session:
        new_user = User(
            id=user_id,
            created_at=datetime.datetime.utcnow(),
            status="alive",
            status_updated_at=datetime.datetime.utcnow(),
            text=text
        )
        session.add(new_user)
        await session.commit()


async def update_user_status(user_id: int, status: str, text: str = None):
    async with async_session() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(
                status=status,
                status_updated_at=datetime.datetime.utcnow(),
                text=text
            )
        )
        await session.commit()


async def get_user(user_id: int):
    async with async_session() as session:
        query = await session.execute(select(User).where(User.id == user_id))
        return query.scalar_one_or_none()


async def get_all_users():
    async with async_session() as session:
        query = await session.execute(select(User))
        return query.scalars().all()

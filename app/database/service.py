from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User


async def check_user_exists(db: AsyncSession):
    """Инициализация таблицы User."""
    stmt = select(exists().where(User.id.isnot(None)))
    await db.scalar(stmt)


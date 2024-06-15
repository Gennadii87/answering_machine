from sqlalchemy import exists, select
from sqlalchemy.orm.exc import NoResultFound
from .database import async_session as session
from .models import User


async def check_user_exists(db: session) -> None:
    """Проверка на существование User."""
    query = select([exists().where(User.id.isnot(None))])
    exists_user = await db.scalar(query)
    if not exists_user:
        raise NoResultFound('User table not found')

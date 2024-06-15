from sqlalchemy import Column, Integer, String, DateTime
import datetime
from database.database import Base


class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="alive")
    status_updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(String, nullable=True)

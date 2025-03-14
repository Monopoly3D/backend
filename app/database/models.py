from datetime import datetime

from sqlalchemy import Column, UUID, func, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(), unique=True, nullable=False)
    password_hash = Column(String(), nullable=False)
    refresh_token = Column(String(), nullable=True, default=None)
    created_at = Column(DateTime(), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)

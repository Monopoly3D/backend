from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, UUID, func, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(), nullable=False)
    created_at = Column(DateTime(), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)

    roles = relationship("UserRole", back_populates="user")


class UserRefreshToken(Base):
    __tablename__ = "user_refresh_tokens"

    user_id = Column(UUID(True), ForeignKey("users.id"), primary_key=True, nullable=False)
    refresh_token = Column(String(), nullable=False)
    created_at = Column(DateTime(), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)


class UserRole(Base):
    __tablename__ = "roles"

    id = Column(UUID(True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(Role), nullable=False)

    user = relationship("User", back_populates="roles")

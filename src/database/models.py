import enum

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, func, Boolean, Text, Table, Enum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Role(enum.Enum):
    """
    Roles users.
    """
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    roles = Column('roles', Enum(Role), default=Role.user)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())
    first_name = Column(String(150), unique=False, nullable=False)
    last_name = Column(String(150), unique=False, nullable=False)
    patroymic = Column(String(150), unique=False)
    phone_number = Column(String(50), unique=False)
    password_checksum = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)

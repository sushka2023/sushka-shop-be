import enum

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, func, Boolean, Text, Table, Enum, Float
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
    patroymic = Column(String(150), unique=False, nullable=True)
    phone_number = Column(String(50), unique=False, nullable=True)
    password_checksum = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)


class BlacklistToken(Base):
    __tablename__ = 'blacklisted_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, nullable=False)
    added_on = Column(DateTime, default=func.now())


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=False, nullable=False)
    description = Column(String(500), unique=False, nullable=False)
    product_category = relationship("ProductCategory", uselist=False, back_populates="product")
    reviews_id = Column('reviews_id', ForeignKey('reviews.id', ondelete='CASCADE'), default=None)
    rating_id = Column('rating_id', ForeignKey('rating.id', ondelete='CASCADE'), default=None)
    promotional = Column(Boolean, default=False)
    new_product = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('product.id', ondelete='CASCADE'), default=None)
    image_url = Column(String(255), unique=True, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    description = Column(String(255), unique=False, nullable=False)


class Price(Base):
    __tablename__ = 'price'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('product.id', ondelete='CASCADE'), default=None)
    weight = Column(String(20), unique=False, nullable=False)
    price = Column(Float, unique=False, nullable=False)
    old_price = Column(Float, unique=False, nullable=False)


class ProductCategory(Base):
    __tablename__ = 'product_categories'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product", back_populates="product_category")
    name = Column(String(100), unique=True, nullable=False)
    is_deleted = Column(Boolean, default=False)

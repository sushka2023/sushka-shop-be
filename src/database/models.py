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


class PaymentType(enum.Enum):
    """
    Payment type.
    """
    cash_on_delivery_np: str = 'cash_on_delivery_np'
    liqpay: str = 'liqpay'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    role = Column('roles', Enum(Role), default=Role.user)
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
    is_active = Column(Boolean, default=False)
    basket = relationship("Basket", uselist=False, back_populates="user")
    orders = relationship("Order", back_populates="user")
    posts = relationship("Post", uselist=False, back_populates="user")
    favorite = relationship("Favorite", uselist=False, back_populates="user")
    cooperation = relationship("Cooperation", uselist=False, back_populates="user")


class BlacklistToken(Base):
    __tablename__ = 'blacklisted_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, nullable=False)
    added_on = Column(DateTime, default=func.now())


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=False, nullable=False)
    description = Column(String(400), unique=False, nullable=False)
    product_category_id = Column(Integer, ForeignKey('product_categories.id'))
    product_category = relationship("ProductCategory", uselist=False, back_populates="product")
    prices = relationship("Price", back_populates="product")
    images = relationship("Image", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    promotional = Column(Boolean, default=False)
    new_product = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_popular = Column(Boolean, default=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('products.id', ondelete='CASCADE'), default=None)
    product = relationship("Product", back_populates="images")
    image_url = Column(String(255), unique=True, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    description = Column(String(255), unique=False, nullable=False)


class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('products.id', ondelete='CASCADE'), default=None)
    product = relationship("Product", back_populates="prices")
    weight = Column(String(20), unique=False, nullable=False)
    price = Column(Float, unique=False, nullable=False)
    old_price = Column(Float, unique=False, nullable=True)
    quantity = Column(Integer, default=1)


class ProductCategory(Base):
    __tablename__ = 'product_categories'
    id = Column(Integer, primary_key=True)
    product = relationship("Product", back_populates="product_category")
    name = Column(String(100), unique=True, nullable=False)
    is_deleted = Column(Boolean, default=False)


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('products.id', ondelete='CASCADE'), default=None)
    product = relationship("Product", back_populates="reviews")
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    image_id = Column('image_id', ForeignKey('images.id', ondelete='CASCADE'), default=None)
    rate = Column(Integer, default=5)
    description = Column(String(255), unique=False, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)


class Basket(Base):
    __tablename__ = 'baskets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="basket")
    basket_items = relationship("BasketItem", uselist=False, back_populates="basket")
    order = relationship("Order", uselist=False, back_populates="basket")


class BasketItem(Base):
    __tablename__ = 'basket_items'
    id = Column(Integer, primary_key=True)
    basket_id = Column(Integer, ForeignKey('baskets.id'))
    basket = relationship("Basket", back_populates="basket_items")
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")
    basket_id = Column(Integer, ForeignKey('baskets.id'))
    basket = relationship("Basket", back_populates="order")
    price_order = Column(Float, unique=False, nullable=False)
    payment_type = Column('payment_type', Enum(PaymentType), default=PaymentType.liqpay)
    created_at = Column('created_at', DateTime, default=func.now())
    confirmation_manager = Column(Boolean, default=False)
    confirmation_pay = Column(Boolean, default=False)
    call_manager = Column(Boolean, default=False)
    #TODO status = maybe ENum...


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")
    nova_poshta = relationship("NovaPoshta", uselist=False, back_populates="post")
    ukr_poshta = relationship("UkrPoshta", uselist=False, back_populates="post")


class NovaPoshta(Base):
    __tablename__ = 'nova_poshta'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="nova_poshta")
    address = Column(String(255), unique=False, nullable=True)


class UkrPoshta(Base):
    __tablename__ = 'ukr_poshta'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    post = relationship("Post", back_populates="ukr_poshta")
    address = Column(String(255), unique=False, nullable=True)


class Favorite(Base):
    __tablename__ = 'favorits'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="favorite")
    favorite_items = relationship("FavoriteItem", uselist=False, back_populates="favorite")


class FavoriteItem(Base):
    __tablename__ = 'favorite_items'
    id = Column(Integer, primary_key=True)
    favorite_id = Column(Integer, ForeignKey('favorits.id'))
    favorite = relationship("Favorite", back_populates="favorite_items")
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product")


class Cooperation(Base):
    __tablename__ = 'cooperations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="cooperation")
    description = Column(String(255), unique=False, nullable=False)
    check = Column(Boolean, default=False)
    created_at = Column('created_at', DateTime, default=func.now())

import enum

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, func, Boolean, Table, Enum, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# Таблиця для зв'язку "багато до багатьох" між Product і ProductSubCategory
product_subcategory_association = Table(
    'product_subcategory_association',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('subcategory_id', Integer, ForeignKey('product_sub_categories.id'))
)


post_ukrposhta_association = Table(
    'post_ukrposhta_association',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('ukr_poshta_id', Integer, ForeignKey('ukr_poshta.id'))
)


post_novaposhta_association = Table(
    'post_novaposhta_association',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('nova_poshta_id', Integer, ForeignKey('nova_poshta.id'))
)


class Role(enum.Enum):
    """
    Roles users.
    """
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class Rating(enum.Enum):
    """
    Star rating.
    """
    five_stars: int = 5
    four_stars: int = 4
    three_stars: int = 3
    two_stars: int = 2
    one_star: int = 1


class ImageType(enum.Enum):
    """
    Image type.
    """
    product: str = 'product'
    review: str = 'review'


class PaymentTypes(enum.Enum):
    """
    Payment types.
    """
    cash_on_delivery_np: str = 'cash_on_delivery_np'
    liqpay: str = 'liqpay'


class ProductStatus(enum.Enum):
    """
    Product status.
    """
    new: str = 'new'
    activated: str = 'activated'
    archived: str = 'archived'

      
class OrderStatus(enum.Enum):
    """
    Status of the order
    """
    new: str = 'new'
    in_processing: str = 'in processing'
    shipped: str = 'shipped'
    delivered: str = 'delivered'
    cancelled: str = 'cancelled'


class UpdateFromDictMixin:
    def update_from_dict(self, data_dict):
        for key, value in data_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


class User(Base, UpdateFromDictMixin):
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

    # Зв'язок з ProductSubCategory через проміжну таблицю
    subcategories = relationship("ProductSubCategory", secondary=product_subcategory_association, back_populates="products")

    prices = relationship("Price", back_populates="product")
    images = relationship("Image", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    new_product = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_popular = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    product_status = Column('product_status', Enum(ProductStatus), default=ProductStatus.new)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('products.id', ondelete='CASCADE'), default=None)
    product = relationship("Product", back_populates="images")
    review_id = Column('review_id', ForeignKey('reviews.id', ondelete='CASCADE'), default=None)
    review = relationship("Review", back_populates="images")
    image_url = Column(String(255), unique=False, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    description = Column(String(255), unique=False, nullable=False)
    image_type = Column('image_type', Enum(ImageType), default=None)
    is_deleted = Column(Boolean, default=False)
    main_image = Column(Boolean, default=False)


class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('products.id', ondelete='CASCADE'), default=None)
    product = relationship("Product", back_populates="prices")
    weight = Column(String(20), unique=False, nullable=False)
    price = Column(Float, unique=False, nullable=False)
    old_price = Column(Float, unique=False, nullable=True)
    quantity = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    promotional = Column(Boolean, default=False)


class ProductCategory(Base):
    __tablename__ = 'product_categories'
    id = Column(Integer, primary_key=True)
    product = relationship("Product", back_populates="product_category")
    name = Column(String(100), unique=True, nullable=False)
    is_deleted = Column(Boolean, default=False)


class ProductSubCategory(Base):
    __tablename__ = 'product_sub_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    is_deleted = Column(Boolean, default=False)

    # Зв'язок з Product через проміжну таблицю
    products = relationship("Product", secondary=product_subcategory_association, back_populates="subcategories")


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    product_id = Column('product_id', ForeignKey('products.id', ondelete='CASCADE'), default=None)
    product = relationship("Product", back_populates="reviews")
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    images = relationship("Image", back_populates="review")
    rating = Column('rating', Enum(Rating), default=Rating.five_stars)
    description = Column(String(255), unique=False, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)
    is_checked = Column(Boolean, default=False)


class Basket(Base):
    __tablename__ = 'baskets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="basket")
    basket_items = relationship("BasketItem", uselist=True, back_populates="basket")
    order = relationship("Order", uselist=False, back_populates="basket")


class BasketItem(Base):
    __tablename__ = 'basket_items'
    id = Column(Integer, primary_key=True)
    basket_id = Column(Integer, ForeignKey('baskets.id'))
    basket = relationship("Basket", back_populates="basket_items")
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product")
    quantity = Column(Integer, default=1)
    price_id_by_the_user = Column(Integer)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")
    basket_id = Column(Integer, ForeignKey('baskets.id'))
    basket = relationship("Basket", back_populates="order")
    price_order = Column(Float, unique=False, nullable=False)
    payment_type = Column('payment_type', Enum(PaymentTypes), default=PaymentTypes.liqpay)
    created_at = Column('created_at', DateTime, default=func.now())
    confirmation_manager = Column(Boolean, default=False)
    confirmation_pay = Column(Boolean, default=False)
    call_manager = Column(Boolean, default=False)
    status_order = Column('status_order', Enum(OrderStatus), default=OrderStatus.new)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")

    ukr_poshta = relationship(
        "UkrPoshta", secondary=post_ukrposhta_association, back_populates="post"
    )
    nova_poshta = relationship(
        "NovaPoshta", secondary=post_novaposhta_association, back_populates="post"
    )


class NovaPoshta(Base):
    __tablename__ = 'nova_poshta'
    id = Column(Integer, primary_key=True)
    office_number = Column(String(255), nullable=False)
    street = Column(String(255), nullable=True)
    house_number = Column(String(255), nullable=True)
    apartment_number = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    region = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)

    post = relationship(
        "Post", secondary=post_novaposhta_association, back_populates="nova_poshta"
    )


class UkrPoshta(Base, UpdateFromDictMixin):
    __tablename__ = 'ukr_poshta'
    id = Column(Integer, primary_key=True)
    street = Column(String(255), nullable=False)
    house_number = Column(String(255), nullable=False)
    apartment_number = Column(String(255), nullable=True)
    city = Column(String(255), nullable=False)
    region = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    post_code = Column(String(255), nullable=False)

    post = relationship(
        "Post", secondary=post_ukrposhta_association, back_populates="ukr_poshta"
    )


class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="favorite")
    favorite_items = relationship("FavoriteItem", uselist=False, back_populates="favorite")


class FavoriteItem(Base):
    __tablename__ = 'favorite_items'
    id = Column(Integer, primary_key=True)
    favorite_id = Column(Integer, ForeignKey('favorites.id'))
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

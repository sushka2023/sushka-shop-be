from typing import List, Type

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from src.database.models import Product, Price, ProductCategory, ProductStatus
from src.schemas.product import ProductModel
from src.services.products import product_with_prices_and_images


async def product_by_name(body: str, db: Session) -> Product | None:
    return db.query(Product).filter_by(name=body).first()


async def product_by_id(body: int, db: Session) -> Product | None:
    product = db.query(Product).filter_by(id=body).first()
    if not product:
        return None
    product_with_price = await product_with_prices_and_images([product], db)
    try:
        product_ = product_with_price[0]
    except Exception as ex:
        return None
    return product_


async def get_products_all_for_crm(db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter().\
        order_by(desc(Product.created_at)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_id(db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter(Product.is_deleted == False, Product.product_status == ProductStatus.activated).\
        order_by(asc(Product.id)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_id_by_category_id(category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category).\
        filter(Product.is_deleted == False, ProductCategory.id == category_id, Product.product_status == ProductStatus.activated).\
        order_by(asc(Product.id)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_name(db: Session):
    products_ = db.query(Product). \
        filter(Product.is_deleted == False, Product.product_status == ProductStatus.activated). \
        order_by(asc(Product.name)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_name_by_category_id(category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id, Product.product_status == ProductStatus.activated).\
        order_by(asc(Product.name)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_low_price(db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price, Product.id == Price.product_id).\
        filter(Product.is_deleted == False, Product.product_status == ProductStatus.activated).\
        order_by(asc(Price.price)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_low_price_by_category_id(category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price, Product.id == Price.product_id).\
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id, Product.product_status == ProductStatus.activated).\
        order_by(asc(Price.price)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_high_price(db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Price, Product.id == Price.product_id). \
        filter(Product.is_deleted == False, Product.product_status == ProductStatus.activated).\
        order_by(desc(Price.price)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_high_price_by_category_id(category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price, Product.id == Price.product_id).\
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id, Product.product_status == ProductStatus.activated).\
        order_by(desc(Price.price)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_low_date(db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter(Product.is_deleted == False, Product.product_status == ProductStatus.activated).\
        order_by(asc(Product.created_at)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_low_date_by_category_id(category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id, Product.product_status == ProductStatus.activated).\
        order_by(asc(Product.created_at)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_high_date(db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter(Product.is_deleted == False, Product.product_status == ProductStatus.activated).\
        order_by(desc(Product.created_at)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def get_products_high_date_by_category_id(category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id, Product.product_status == ProductStatus.activated).\
        order_by(desc(Product.created_at)).\
        all()

    product_with_price = await product_with_prices_and_images(products_, db)

    return product_with_price


async def create_product(body: dict, db: Session) -> Type[Product]:
    new_product = Product(**body)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


async def archive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.product_status = ProductStatus.archived
        product.is_deleted = True
        db.commit()
        return product
    return None


async def unarchive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.product_status = ProductStatus.new
        product.is_deleted = False
        db.commit()
        return product
    return None

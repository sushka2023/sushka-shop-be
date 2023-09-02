from typing import List, Type

from sqlalchemy import desc, asc, nullslast, select, func
from sqlalchemy.orm import Session

from src.database.models import Product, Price, ProductCategory
from src.schemas.product import ProductModel


async def product_by_name(body: str, db: Session) -> Product | None:
    return db.query(Product).filter_by(name=body).first()


async def product_by_id(body: int, db: Session) -> Product | None:
    return db.query(Product).filter_by(id=body).first()


async def get_products_id(limit: int, offset: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter(Product.is_deleted == False).\
        order_by(asc(Product.id)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_id_by_category_id(limit: int, offset: int, category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category).\
        filter(Product.is_deleted == False, ProductCategory.id == category_id).\
        order_by(asc(Product.id)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_



async def get_products_name(limit: int, offset: int, db: Session):
    subquery = (
        select(Price.product_id, func.min(Price.price).label("lowest_price"))
        .group_by(Price.product_id)
        .subquery()
    )

    products_with_price = db.query(Product, subquery.c.lowest_price).\
        outerjoin(subquery, Product.id == subquery.c.product_id).\
        filter(Product.is_deleted == False).\
        order_by(asc(Product.name)).\
        limit(limit).\
        offset(offset).\
        all()



async def get_products_name_by_category_id(limit: int, offset: int, category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id).\
        order_by(asc(Product.name)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_

    print(products_with_price)
    return products_with_price

# async def get_products_name(limit: int, offset: int, db: Session) -> List[Type[Product]] | None:
#     products_ = db.query(Product).\
#         filter(Product.is_deleted == False).\
#         order_by(asc(Product.name)).\
#         limit(limit).\
#         offset(offset).\
#         all()
#     return products_

async def get_products_low_price(limit: int, offset: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price).\
        filter(Product.is_deleted == False).\
        order_by(asc(Price.price)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_low_price_by_category_id(limit: int, offset: int, category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id).\
        order_by(asc(Price.price)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_high_price(limit: int, offset: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price).\
        filter(Product.is_deleted == False).\
        order_by(desc(Price.price)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_high_price_by_category_id(limit: int, offset: int, category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        join(Price). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id).\
        order_by(desc(Price.price)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_low_date(limit: int, offset: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter(Product.is_deleted == False).\
        order_by(asc(Product.created_at)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_low_date_by_category_id(limit: int, offset: int, category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id).\
        order_by(asc(Product.created_at)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_high_date(limit: int, offset: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product).\
        filter(Product.is_deleted == False).\
        order_by(desc(Product.created_at)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def get_products_high_date_by_category_id(limit: int, offset: int, category_id: int, db: Session) -> List[Type[Product]] | None:
    products_ = db.query(Product). \
        join(Product.product_category). \
        filter(Product.is_deleted == False, ProductCategory.id == category_id).\
        order_by(desc(Product.created_at)).\
        limit(limit).\
        offset(offset).\
        all()
    return products_


async def create_product(body: ProductModel, db: Session) -> Product:
    new_product = Product(**body.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


async def archive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.is_deleted = True
        db.commit()
        return product
    return None


async def unarchive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.is_deleted = False
        db.commit()
        return product
    return None

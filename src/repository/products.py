from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from src.database.models import Product, Price
from src.schemas.product import ProductModel


async def product_by_name(body: str, db: Session) -> Product | None:
    return db.query(Product).filter_by(name=body).first()


async def product_by_id(body: int, db: Session) -> Product | None:
    return db.query(Product).filter_by(id=body).first()


async def get_products(limit: int, offset: int, sort: str, db: Session) -> List[Product] | None:
    if "id" in sort:
        products_ = db.query(Product).filter(Product.is_deleted == False).order_by(asc(Product.id)).limit(limit).offset(offset).all()
    elif "name" in sort:
        products_ = db.query(Product).filter(Product.is_deleted == False).order_by(asc(Product.name)).limit(limit).offset(offset).all()
    elif "low_price" in sort:
        products_ = db.query(Product).outerjoin(Price).filter(Product.is_deleted == False).order_by(asc(Price.price)).limit(limit).offset(offset).all()
    elif "haigh_price" in sort:
        products_ = db.query(Product).outerjoin(Price).filter(Product.is_deleted == False).order_by(desc(Price.price)).limit(limit).offset(offset).all()
    elif "low_date" in sort:
        products_ = db.query(Product).filter(Product.is_deleted == False).order_by(asc(Product.created_at)).limit(limit).offset(offset).all()
    elif "haigh_date" in sort:
        products_ = db.query(Product).filter(Product.is_deleted == False).order_by(desc(Product.created_at)).limit(limit).offset(offset).all()
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


async def return_archive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.is_deleted = False
        db.commit()
        return product
    return None

from typing import List

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from src.database.models import Product
from src.schemas.product import ProductModel


async def product_by_name(body: str, db: Session) -> Product | None:
    return db.query(Product).filter_by(name=body).first()


async def product_by_id(body: int, db: Session) -> Product | None:
    return db.query(Product).filter_by(id=body).first()


async def products_users_order_id(limit: int, offset: int, db: Session) -> List[Product] | None:
    products_ = db.query(Product).filter(Product.is_deleted == False).order_by(asc(Product.id)).limit(limit).offset(offset).all()
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

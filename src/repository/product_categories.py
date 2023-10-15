from typing import List, Type

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc

from src.database.models import ProductCategory
from src.schemas.product_category import ProductCategoryModel, ProductCategoryResponse, ProductCategoryArchiveModel, \
    ProductCategoryEditModel


async def product_category_by_name(body: str, db: Session) -> ProductCategory | None:
    return db.query(ProductCategory).filter_by(name=body).first()


async def product_category_by_id(body: int, db: Session) -> ProductCategory | None:
    return db.query(ProductCategory).filter_by(id=body).first()


async def product_categories(db: Session) -> List[Type[ProductCategory]] | None:
    prod_categories = db.query(ProductCategory).filter((ProductCategory.is_deleted == False)).\
        order_by(asc(ProductCategory.name)).all()
    return prod_categories


async def product_categories_all_for_crm(db: Session) -> List[Type[ProductCategory]] | None:
    prod_categories = db.query(ProductCategory).order_by(asc(ProductCategory.name)).all()
    return prod_categories


async def create_product_category(body: ProductCategoryModel, db: Session) -> ProductCategory:
    new_product_category = ProductCategory(**body.dict())
    db.add(new_product_category)
    db.commit()
    db.refresh(new_product_category)
    return new_product_category


async def edit_product_category(body: ProductCategoryEditModel, product_category: ProductCategory, db: Session) -> ProductCategory:
    product_category.name = body.name
    db.commit()
    db.refresh(product_category)
    return product_category


async def archive_product_category(body: int, db: Session) -> Type[ProductCategory] | None:
    product_category = db.query(ProductCategory).filter_by(id=body).first()
    if product_category:
        product_category.is_deleted = True
        db.commit()
        return product_category
    return None


async def unarchive_product_category(body: int, db: Session) -> Type[ProductCategory] | None:
    product_category = db.query(ProductCategory).filter_by(id=body).first()
    if product_category:
        product_category.is_deleted = False
        db.commit()
        return product_category
    return None

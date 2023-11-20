from typing import List, Type

from sqlalchemy.orm import Session
from sqlalchemy import asc, create_engine, text

from src.database.db import engine
from src.database.models import ProductSubCategory
from src.schemas.product_sub_category import ProductSubCategoryModel, ProductSubCategoryEditModel


async def product_sub_category_by_name(body: str, db: Session) -> ProductSubCategory | None:
    return db.query(ProductSubCategory).filter_by(name=body).first()


async def product_sub_category_by_id(body: int, db: Session) -> ProductSubCategory | None:
    return db.query(ProductSubCategory).filter_by(id=body).first()


async def product_sub_categories(db: Session) -> List[Type[ProductSubCategory]] | None:
    prod_categories = db.query(ProductSubCategory).filter((ProductSubCategory.is_deleted == False)).\
        order_by(asc(ProductSubCategory.name)).all()
    return prod_categories


async def product_sub_categories_all_for_crm(db: Session) -> List[Type[ProductSubCategory]] | None:
    prod_categories = db.query(ProductSubCategory).order_by(asc(ProductSubCategory.name)).all()
    return prod_categories


async def create_sub_product_category(body: ProductSubCategoryModel, db: Session) -> ProductSubCategory:
    new_product_category = ProductSubCategory(**body.dict())
    db.add(new_product_category)
    db.commit()
    db.refresh(new_product_category)
    return new_product_category


async def edit_sub_product_category(body: ProductSubCategoryEditModel, product_category: ProductSubCategory, db: Session) -> ProductSubCategory:
    product_category.name = body.name
    db.commit()
    db.refresh(product_category)
    return product_category


async def archive_sub_product_category(body: int, db: Session) -> Type[ProductSubCategory] | None:
    product_category = db.query(ProductSubCategory).filter_by(id=body).first()
    if product_category:
        product_category.is_deleted = True
        db.commit()
        return product_category
    return None


async def unarchive_sub_product_category(body: int, db: Session) -> Type[ProductSubCategory] | None:
    product_category = db.query(ProductSubCategory).filter_by(id=body).first()
    if product_category:
        product_category.is_deleted = False
        db.commit()
        return product_category
    return None


async def insert_sub_category_for_product(product_id: int, sub_categories_ids: List[int], db: Session):
    if len(sub_categories_ids) == 0:
        return None

    for sub_id in sub_categories_ids:
        # SQL-запит для вставки даних
        insert_query = text(
            "INSERT INTO product_subcategory_association (product_id, subcategory_id) "
            "VALUES (:product_id, :subcategory_id)"
        )

        with engine.connect() as connection:
            connection.execute(insert_query, {"product_id": product_id, "subcategory_id": sub_id})
            connection.commit()
    return None

from sqlalchemy.orm import Session

from src.database.models import ProductCategory
from src.schemas.product_category import ProductCategoryModel, ProductCategoryResponse, ProductCategoryArchiveModel


async def product_category_by_name(body: str, db: Session) -> ProductCategory | None:
    return db.query(ProductCategory).filter_by(name=body).first()


async def product_category_by_id(body: int, db: Session) -> ProductCategory | None:
    return db.query(ProductCategory).filter_by(id=body).first()


async def create_product_category(body: ProductCategoryModel, db: Session) -> ProductCategory:
    new_product_category = ProductCategory(**body.dict())
    db.add(new_product_category)
    db.commit()
    db.refresh(new_product_category)
    return new_product_category


async def archive_product_category(body: int, db: Session) -> ProductCategory | None:
    product_category = db.query(ProductCategory).filter_by(id=body).first()
    if product_category:
        product_category.is_deleted = True
        db.commit()
        return product_category
    return None


async def return_archive_product_category(body: int, db: Session) -> ProductCategory | None:
    product_category = db.query(ProductCategory).filter_by(id=body).first()
    if product_category:
        product_category.is_deleted = False
        db.commit()
        return product_category
    return None

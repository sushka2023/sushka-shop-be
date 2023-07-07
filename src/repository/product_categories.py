from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import ProductCategory
from src.schemas.product_category import ProductCategoryModel
from src.services.auth import auth_service


async def product_category_by_name(body: str, db: Session) -> ProductCategory | None:
    return db.query(ProductCategory).filter_by(name=body).first()


async def create_product_category(body: ProductCategoryModel, db: Session) -> ProductCategory:
    new_product_category = ProductCategory(**body.dict())
    db.add(new_product_category)
    db.commit()
    db.refresh(new_product_category)
    return new_product_category

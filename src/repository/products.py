from sqlalchemy.orm import Session

from src.database.models import Product
from src.schemas.product import ProductModel


async def product_by_name(body: str, db: Session) -> Product | None:
    return db.query(Product).filter_by(name=body).first()


async def create_product(body: ProductModel, db: Session) -> Product:
    new_product = Product(**body.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

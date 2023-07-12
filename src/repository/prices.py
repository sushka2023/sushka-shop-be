from typing import List

from sqlalchemy.orm import Session

from src.database.models import Price
from src.schemas.price import PriceModel, PriceResponse


async def price_by_product_id(id_product: int, db: Session) -> List[PriceResponse]:
    price = db.query(Price).filter_by(product_id=id_product).all()
    return price


async def price_by_id(id_price: int, db: Session) -> PriceResponse:
    price = db.query(Price).filter_by(id=id_price).first()
    return price


async def create_price(body: PriceModel, db: Session) -> PriceResponse:
    new_price = Price(**body.dict())
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price


async def archive_price(body: int, db: Session):
    price = db.query(Price).filter_by(id=body).first()
    if price:
        price.is_deleted = True
        db.commit()
        return price
    return None


async def unarchive_price(body: int, db: Session):
    price = db.query(Price).filter_by(id=body).first()
    if price:
        price.is_deleted = False
        db.commit()
        return price
    return None

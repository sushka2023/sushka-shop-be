from typing import List

from sqlalchemy.orm import Session

from src.database.models import Price
from src.schemas.price import PriceModel, PriceResponse


async def price_by_product_id(id_product: int, db: Session) -> List[PriceResponse]:
    price = db.query(Price).filter_by(product_id=id_product).all()
    return price


async def create_price(body: PriceModel, db: Session) -> PriceResponse:
    new_price = Price(**body.dict())
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price

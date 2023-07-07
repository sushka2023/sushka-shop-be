from sqlalchemy.orm import Session

from src.database.models import Price
from src.schemas.price import PriceModel, PriceResponse


async def price_by_product_id(body: int, db: Session) -> [PriceResponse]:
    return db.query(Price).filter_by(product_id=body).all()


async def create_price(body: PriceModel, db: Session) -> PriceResponse:
    new_price = Price(**body.dict())
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price

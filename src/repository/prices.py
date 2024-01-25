from typing import List, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, asc

from src.database.models import Price, Product
from src.schemas.price import PriceModel, PriceResponse
from src.services.exception_detail import ExDetail as Ex


async def price_by_product_id(id_product: int, db: Session) -> List[Type[PriceResponse]]:
    price = db.query(Price).filter_by(product_id=id_product, is_deleted=False).all()
    return price


async def price_by_product(product: Type[Product], db: Session) -> List[Type[PriceResponse]]:
    prices_in_ascending_order = (db.query(Price).
                                 filter(Price.product == product).
                                 order_by(asc(Price.price)).
                                 all())
    return prices_in_ascending_order


async def price_by_id(id_price: int, db: Session) -> Type[Price]:
    price = db.query(Price).filter_by(id=id_price).first()
    return price


async def price_by_product_id_and_price_id(product_id: int, price_id: int, db: Session) -> Price:
    return db.query(Price).filter(
        Price.product_id == product_id, Price.id == price_id, Price.is_deleted == False
    ).first()


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


async def calculate_total_price(price_ids: List[int], db: Session) -> str:
    total_price = (
        db.query(func.sum(Price.price))
        .filter(Price.id.in_(price_ids))
        .filter(Price.is_deleted == False)
        .scalar()
    )
    if total_price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    total_price = '{:.2f}'.format(total_price)
    return total_price or "0.00"

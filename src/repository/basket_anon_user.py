import logging

from typing import Optional, Type

from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models import BasketAnonUser, Product
from src.schemas.basket_anon_user import BasketAnonUserModel, BasketAnonUserRemoveModel


logger = logging.getLogger(__name__)


async def create_basket(
        db: Session, product_id: int, price_id_by_anon_user: int, quantity: int
):
    new_basket_anon_user = BasketAnonUser(
        product_id=product_id,
        quantity=quantity,
        price_id_by_anon_user=price_id_by_anon_user
    )
    db.add(new_basket_anon_user)
    db.commit()
    db.refresh(new_basket_anon_user)
    return new_basket_anon_user


async def get_existing_basket_anon_user(product_id: int, db: Session) -> Optional[BasketAnonUser]:
    return db.query(BasketAnonUser).filter(BasketAnonUser.product_id == product_id).first()


async def update_basket(body: BasketAnonUserModel, db: Session):
    existing_basket_item = await get_existing_basket_anon_user(body.product_id, db)

    if existing_basket_item:
        existing_basket_item.quantity += body.quantity
        existing_basket_item.price_id_by_anon_user = body.price_id_by_anon_user
        db.commit()
        db.refresh(existing_basket_item)
        return existing_basket_item


async def basket_item_anon_user(
        body: BasketAnonUserRemoveModel, db: Session, price_id_by_anon_user: int = None
) -> Type[BasketAnonUser] | None:
    query = db.query(BasketAnonUser).filter(BasketAnonUser.product_id == body.product_id)

    if price_id_by_anon_user is not None:
        query = query.filter(BasketAnonUser.price_id_by_anon_user == price_id_by_anon_user)

    return query.first()


async def basket_items_anon_user(db: Session) -> list[BasketAnonUser] | None:
    basket_items = (
        db.query(BasketAnonUser)
        .join(Product, Product.id == BasketAnonUser.product_id)
        .order_by(asc(Product.name))
        .all()
    )
    return basket_items


async def get_basket_item_by_id(basket_item_id: int, db: Session) -> Type[BasketAnonUser] | None:
    return db.query(BasketAnonUser).filter(BasketAnonUser.id == basket_item_id).first()


async def update_quantity(basket_item: Type[BasketAnonUser], quantity: int, db) -> Type[BasketAnonUser] | None:
    if basket_item:
        basket_item.quantity = quantity
        db.commit()
        db.refresh(basket_item)
        return basket_item
    return None


async def get_basket_item_by_product_id(product_id: int, db: Session):
    basket_item = db.query(BasketAnonUser).filter(
        BasketAnonUser.product_id == product_id
    ).first()
    return basket_item


async def remove_item(basket_item: BasketAnonUser, db: Session):
    try:
        db.delete(basket_item)
        db.commit()
    except SQLAlchemyError as e:
        logger.exception("SQLAlchemyError")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def delete_basket_items_anon_user(db: Session):
    """Anon User Shopping Cart Cleaning"""
    try:
        db.query(BasketAnonUser).delete()
        db.commit()
    except SQLAlchemyError as e:
        logger.exception("SQLAlchemyError")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

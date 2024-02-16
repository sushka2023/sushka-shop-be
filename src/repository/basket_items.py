from typing import List, Optional, Type

from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session


from src.database.models import BasketItem, User, Basket, Product
from src.schemas.basket_items import BasketItemsModel


async def create(
        db: Session,
        basket_id: int,
        product_id: int,
        quantity: int,
        price_id_by_the_user: int
):
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid quantity. Product quantity must be greater than 0."
        )

    new_basket_item = BasketItem(
        basket_id=basket_id,
        product_id=product_id,
        quantity=quantity,
        price_id_by_the_user=price_id_by_the_user
    )
    db.add(new_basket_item)
    db.commit()
    db.refresh(new_basket_item)
    return new_basket_item


async def get_existing_basket_item(basket: Basket, product_id: int, price_id: int, db: Session) -> Optional[BasketItem]:
    return db.query(BasketItem).filter(
        BasketItem.basket_id == basket.id,
        BasketItem.product_id == product_id,
        BasketItem.price_id_by_the_user == price_id,
    ).first()


async def update(body: BasketItemsModel, basket: Basket, db: Session):
    existing_basket_item = await get_existing_basket_item(basket, body.product_id, body.price_id_by_the_user, db)

    if existing_basket_item:
        existing_basket_item.quantity += body.quantity
        db.commit()
        db.refresh(existing_basket_item)
        return existing_basket_item


async def basket_items(current_user: User, db: Session) -> List[BasketItem] | None:
    basket_items_ = db.query(BasketItem.id, BasketItem.basket_id, BasketItem.product_id, BasketItem.quantity, BasketItem.price_id_by_the_user) \
        .join(Basket, Basket.id == BasketItem.basket_id) \
        .join(Product, Product.id == BasketItem.product_id) \
        .filter(Basket.user_id == current_user.id) \
        .order_by(asc(Product.name)) \
        .all()
    return basket_items_


async def basket_item(
        body: BasketItemsModel, current_user: User, db: Session, price_id_by_the_user: int = None
) -> Type[BasketItem] | None:
    query = db.query(BasketItem).join(Basket).filter(
        BasketItem.product_id == body.product_id,
        Basket.user_id == current_user.id
    )

    if price_id_by_the_user is not None:
        query = query.filter(BasketItem.price_id_by_the_user == price_id_by_the_user)

    return query.first()


async def basket_item_for_id(basket_item_id: int, db: Session) -> Type[BasketItem] | None:
    return db.query(BasketItem).filter(BasketItem.id == basket_item_id).first()


async def remove(basket_item_: BasketItem, db: Session):
    db.delete(basket_item_)
    db.commit()
    return None


async def update_quantity(basket_item_: Type[BasketItem], quantity: int, db) -> Type[BasketItem] | None:
    if basket_item_:
        basket_item_.quantity = quantity
        db.commit()
        db.refresh(basket_item_)
        return basket_item_
    return None

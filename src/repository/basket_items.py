from typing import List, Optional, Type

from sqlalchemy import asc
from sqlalchemy.orm import Session


from src.database.models import BasketItem, User, Basket, Product
from src.schemas.basket_items import BasketItemsModel, BasketItemsRemoveModel


async def create(body: BasketItemsModel, basket: Basket, db: Session) -> BasketItem:
    new_basket_item = BasketItem(basket_id=basket.id,
                                 product_id=body.product_id,
                                 quantity=body.quantity,
                                 price_id_by_the_user=body.price_id_by_the_user)
    db.add(new_basket_item)
    db.commit()
    db.refresh(new_basket_item)
    return new_basket_item


async def get_existing_basket_item(basket: Basket, product_id: int, db: Session) -> Optional[BasketItem]:
    return db.query(BasketItem).filter(
        BasketItem.basket_id == basket.id,
        BasketItem.product_id == product_id
    ).first()


async def update(body: BasketItemsModel, basket: Basket, db: Session):
    existing_basket_item = await get_existing_basket_item(basket, body.product_id, db)

    if existing_basket_item:
        existing_basket_item.quantity += body.quantity
        existing_basket_item.price_id_by_the_user = body.price_id_by_the_user
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


async def basket_item(body: BasketItemsRemoveModel, current_user: User, db: Session) -> Type[BasketItem] | None:
    return db.query(BasketItem).join(Basket).filter(
        BasketItem.product_id == body.product_id,
        Basket.user_id == current_user.id
    ).first()


async def basket_item_for_id(basket_item_id: int, db: Session) -> Type[BasketItem] | None:
    return db.query(BasketItem).filter(BasketItem.id == basket_item_id).first()


async def get_b_item_from_product_id(product_id: int, basket_id: int, db: Session):
    basket_item_ = db.query(BasketItem).filter(BasketItem.product_id == product_id, BasketItem.basket_id == basket_id).first()
    return basket_item_


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

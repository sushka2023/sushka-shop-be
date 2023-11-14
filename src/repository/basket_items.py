from typing import List

from sqlalchemy import asc
from sqlalchemy.orm import Session


from src.database.models import BasketItem, User, Basket, Product
from src.schemas.basket_items import BasketItemsModel


async def create(body: BasketItemsModel, basket: Basket, db: Session):
    new_basket_item = BasketItem(basket_id=basket.id, product_id=body.product_id, quantity=body.quantity)
    db.add(new_basket_item)
    db.commit()
    db.refresh(new_basket_item)
    return new_basket_item


async def update(body: BasketItemsModel, basket: Basket, db: Session):
    existing_basket_item = db.query(BasketItem).filter(
        BasketItem.basket_id == basket.id,
        BasketItem.product_id == body.product_id
    ).first()

    if existing_basket_item:
        existing_basket_item.quantity += body.quantity
        db.commit()
        db.refresh(existing_basket_item)
        return existing_basket_item


async def basket_items(current_user: User, db: Session) -> List[BasketItem] | None:
    basket_items_ = db.query(BasketItem.id, BasketItem.basket_id, BasketItem.product_id, BasketItem.quantity) \
        .join(Basket, Basket.id == BasketItem.basket_id) \
        .join(Product, Product.id == BasketItem.product_id) \
        .filter(Basket.user_id == current_user.id) \
        .order_by(asc(Product.name)) \
        .all()
    return basket_items_


async def basket_item(body: BasketItemsModel, current_user: User, db: Session) -> BasketItem:
    return db.query(BasketItem).join(Basket).filter(
        BasketItem.product_id == body.product_id,
        Basket.user_id == current_user.id
    ).first()


async def get_b_item_from_product_id(product_id: int, db: Session):
    basket_item_ = db.query(BasketItem).filter(product_id == product_id).first()
    return basket_item_


async def remove(basket_item_: BasketItem, db: Session):
    db.delete(basket_item_)
    db.commit()
    return None

from typing import List

from sqlalchemy import asc
from sqlalchemy.orm import Session


from src.database.models import BasketItem, User, Basket, Product
from src.schemas.basket_items import BasketItemsModel


async def create(body: BasketItemsModel, basket: Basket, db: Session):
    new_basket_item = BasketItem(basket_id=basket.id, product_id=body.product_id)
    db.add(new_basket_item)
    db.commit()
    db.refresh(new_basket_item)
    return new_basket_item


async def basket_items(current_user: User, db: Session) -> List[Basket] | None:  #TODO Basket or BasketItems
    basket_items_ = db.query(BasketItem.id, BasketItem.basket_id, BasketItem.product_id) \
        .join(Basket, Basket.id == BasketItem.basket_id) \
        .join(Product, Product.id == BasketItem.product_id) \
        .filter(Basket.user_id == current_user.id) \
        .order_by(Product.name.asc()) \
        .all()
    return basket_items_


async def basket_item(body: BasketItemsModel, current_user: User, db: Session) -> Product:
    basket_item_ = db.query(BasketItem.id, BasketItem.basket_id, BasketItem.product_id) \
        .join(Basket, Basket.id == BasketItem.basket_id) \
        .join(Product, Product.id == BasketItem.product_id) \
        .filter(BasketItem.product_id == body.product_id, Basket.user_id == current_user.id) \
        .order_by(Product.name.asc()) \
        .first()
    return basket_item_


async def get_b_item_from_product_id(product_id: int, db: Session):
    basket_item_ = db.query(BasketItem).filter(product_id == product_id).first()
    return basket_item_


async def remove(basket_item_: BasketItem, db: Session):
    db.delete(basket_item_)
    db.commit()
    return None

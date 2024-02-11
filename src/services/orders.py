import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models import Basket, OrderedProduct, BasketItem


logger = logging.getLogger(__name__)


async def calculate_basket_total_cost(basket: Basket):
    """Determination of total order value"""

    total_cost = 0.0

    if basket.basket_items:
        for basket_item in basket.basket_items:
            product = basket_item.product
            price = next(
                (p for p in product.prices if p.id == basket_item.price_id_by_the_user),
                None
            )

            if price:
                total_cost += float(price.price * basket_item.quantity)

    return total_cost


async def get_items_by_order_id(order_id: int, db: Session):
    return db.query(OrderedProduct).filter(OrderedProduct.order_id == order_id)


async def calculate_basket_total_cost_for_anonym_user(order_id: int, db: Session):
    """Determination of total order value for anonym user"""

    total_cost_order = 0.0

    order_items = await get_items_by_order_id(order_id=order_id, db=db)

    if order_items:
        for item in order_items:
            product = item.products
            price = next(
                (p for p in product.prices if p.id == item.price_id),
                None
            )

            if price:
                total_cost_order += float(price.price * item.quantity)

    return total_cost_order


async def move_product_to_ordered(db: Session, basket_item: BasketItem) -> OrderedProduct | None:
    ordered_product = OrderedProduct(
        product_id=basket_item.product_id,
        price_id=basket_item.price_id_by_the_user,
        quantity=basket_item.quantity
    )
    db.add(ordered_product)
    db.commit()
    db.refresh(ordered_product)

    if ordered_product.id is not None:
        return ordered_product
    else:
        return None


async def delete_basket_items_by_basket_id(basket_id: int, db: Session):
    """User Shopping Cart Cleaning"""
    try:
        db.query(BasketItem).filter(BasketItem.basket_id == basket_id).delete()
        db.commit()
    except SQLAlchemyError as e:
        logger.exception("SQLAlchemyError")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

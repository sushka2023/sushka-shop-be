from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from src.database.models import Basket, User, Order, BasketItem, OrderStatus
from src.repository.prices import price_by_product_id
from src.schemas.orders import OrderModel


async def calculate_basket_total_cost(basket: Basket, db: Session):
    """Determination of total order value"""

    total_cost = 0.0

    if basket.basket_items:
        for basket_item in basket.basket_items:
            product = basket_item.product
            prices = await price_by_product_id(product.id, db)
            if prices:
                for price in prices:
                    total_cost += float(price.price * basket_item.quantity)

    return total_cost


async def get_order_by_id(order_id: int, db: Session) -> Order | None:
    return db.query(Order).filter_by(id=order_id).first()


async def get_orders_by_user(limit: int, offset: int, user: User, db: Session) -> list[Order]:
    return (
        db.query(Order).filter(Order.user_id == user.id)
        .order_by(desc(Order.created_at)).limit(limit).offset(offset).all()
    )


async def get_orders_for_crm(limit: int, offset: int, db: Session) -> list[Order]:
    return db.query(Order).order_by(desc(Order.created_at)).limit(limit).offset(offset).all()


async def get_user_with_basket_and_items(user_id: int, db: Session) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.basket).joinedload(Basket.basket_items)
        )
        .filter(User.id == user_id)
        .first()
    )
    return user


async def delete_basket_items_by_basket_id(basket_id: int, db: Session):
    """User Shopping Cart Cleaning"""
    db.query(BasketItem).filter(BasketItem.basket_id == basket_id).delete()
    db.commit()


async def create_order(order_data: OrderModel, user_id: int, db: Session):
    """Create an order and clean the user’s shopping cart after creating an order"""

    user = await get_user_with_basket_and_items(user_id, db)

    if not user.basket:
        user.basket = Basket()

    total_cost = await calculate_basket_total_cost(user.basket, db)

    order = Order(
        user_id=user.id,
        basket_id=user.basket.id,
        price_order=total_cost,
        payment_type=order_data.payment_type,
        call_manager=order_data.call_manager,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    await delete_basket_items_by_basket_id(user.basket.id, db)

    return order


async def confirm_order(order_id: int, db: Session) -> Order | None:
    """Confirmation of user order by admin and changing order status"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order and order.confirmation_manager is False:
        order.confirmation_manager = True
        order.status_order = OrderStatus.in_processing
        db.commit()
        return order
    return None

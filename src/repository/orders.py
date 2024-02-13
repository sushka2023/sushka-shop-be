import logging
from typing import Optional

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload, selectinload

from src.database.models import (
    Basket,
    User,
    Order,
    OrdersStatus,
    OrderedProduct,
    Price,
)
from src.schemas.orders import (
    OrderModel,
    OrderAnonymUserModel,
    OrderItemsModel,
    UpdateOrderStatus
)

from src.services.orders import (
    delete_basket_items_by_basket_id,
    calculate_basket_total_cost,
    calculate_basket_total_cost_for_anonym_user,
    move_product_to_ordered,
)
from src.repository import prices as repository_prices
from src.services.validation import validate_phone_number
from src.services.exception_detail import ExDetail as Ex

logger = logging.getLogger(__name__)


async def get_order_by_id(order_id: int, db: Session) -> Order | None:
    return db.query(Order).filter(Order.id == order_id, Order.is_created == True).first()


async def get_orders_by_auth_user(
        limit: int, offset: int, user: User, db: Session
) -> list[Order]:
    return (
        db.query(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.ordered_products)
            .selectinload(OrderedProduct.prices)
            .options(
                joinedload(Price.product),
                joinedload(Price.ordered_products)
            )
        )
        .filter(OrderedProduct.order_id == Order.id)
        .filter(Price.id == OrderedProduct.price_id)
        .filter(Order.user_id == user.id)
        .order_by(desc(Order.created_at))
        .limit(limit).offset(offset)
        .all()
    )


async def get_orders_auth_user_for_crm(
        limit: int, offset: int, db: Session
) -> list[Order]:
    return (
        db.query(Order).filter(Order.is_authenticated)
        .order_by(desc(Order.created_at))
        .limit(limit).offset(offset).all()
    )


async def get_orders_anonym_user_for_crm(
        limit: int, offset: int, db: Session
) -> list[Order]:
    return (
        db.query(Order).filter(Order.is_authenticated == False)
        .order_by(desc(Order.created_at))
        .limit(limit).offset(offset).all()
    )


async def get_auth_user_with_basket_and_items(user_id: int, db: Session) -> User:
    user = (
        db.query(User)
        .options(
            joinedload(User.basket).joinedload(Basket.basket_items)
        )
        .filter(User.id == user_id)
        .first()
    )
    return user


async def create_order_auth_user(order_data: OrderModel, user_id: int, db: Session):
    """Create an order and clean the user’s shopping cart after creating an order"""

    user = await get_auth_user_with_basket_and_items(user_id, db)

    if not user.basket:
        user.basket = Basket()

    total_cost = await calculate_basket_total_cost(user.basket)

    ordered_products = []
    for basket_item in user.basket.basket_items:
        ordered_product = await move_product_to_ordered(db, basket_item)

        selected_price = await repository_prices.price_by_product_id_and_price_id(
            ordered_product.product_id, ordered_product.price_id, db
        )

        if selected_price:
            ordered_product.prices = selected_price

        ordered_products.append(ordered_product)

    order = Order(
        user_id=user.id,
        user=user,
        basket_id=user.basket.id,
        price_order=total_cost,
        payment_type=order_data.payment_type,
        call_manager=order_data.call_manager,
        ordered_products=ordered_products
    )
    order.is_authenticated = True
    order.is_created = True

    db.add(order)
    db.commit()
    db.refresh(order)

    await delete_basket_items_by_basket_id(user.basket.id, db)

    return order


async def create_order_number_anon_user(db: Session) -> Order:
    new_order = Order()
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


async def get_order_anon_user_by_id(order_id: int, db: Session) -> Order | None:
    return db.query(Order).filter(
        Order.id == order_id,
        Order.is_authenticated == False,
        Order.is_created == False
    ).first()


async def add_items_to_order_anon_user(
        order_id: int, product_id: int, price_id: int, quantity: int, db: Session
) -> OrderedProduct:
    order_anon_user = await get_order_anon_user_by_id(order_id=order_id, db=db)

    new_order_item = OrderedProduct(
        order_id=order_anon_user.id,
        product_id=product_id,
        price_id=price_id,
        quantity=quantity,
    )
    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)
    return new_order_item


async def get_existing_order_item(
        order_id: int, product_id: int, price_id: int, db: Session
) -> Optional[OrderedProduct]:
    return db.query(OrderedProduct).filter(
        OrderedProduct.order_id == order_id,
        OrderedProduct.product_id == product_id,
        OrderedProduct.price_id == price_id,
    ).first()


async def update_quantity_item(body: OrderItemsModel, order_id: int, db: Session):
    existing_order_item = await get_existing_order_item(order_id, body.product_id, body.price_id, db)

    if existing_order_item:
        existing_order_item.quantity += body.quantity
        db.commit()
        db.refresh(existing_order_item)
        return existing_order_item


async def get_order_item(
        order_id: int, product_id: int, price_id: int, db: Session
) -> OrderedProduct | None:
    query = db.query(OrderedProduct).filter(
        OrderedProduct.order_id == order_id,
        OrderedProduct.product_id == product_id,
        OrderedProduct.price_id == price_id
    )

    return query.first()


async def get_order_items(order_id: int, db: Session) -> list[OrderedProduct]:
    return db.query(OrderedProduct).filter(OrderedProduct.order_id == order_id)


async def create_order_anonym_user(
        order_data: OrderAnonymUserModel, order_id: str, db: Session
):
    """Create an order of the anonym user"""

    order_anon_user = await get_order_anon_user_by_id(order_id=int(order_id), db=db)

    if not order_anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    total_cost_order_anon_user = (
        await calculate_basket_total_cost_for_anonym_user(order_id=order_anon_user.id, db=db)
    )

    order_items = await get_order_items(order_id=order_anon_user.id, db=db)

    ordered_products = []
    for order_item in order_items:
        selected_price = await repository_prices.price_by_product_id_and_price_id(
            order_item.product_id, order_item.price_id, db
        )

        if selected_price:
            order_item.prices = selected_price

        ordered_products.append(order_item)

    try:
        validate_phone_number(order_data.phone_number_anon_user)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    order_anon_user.update_from_dict(order_data.dict())
    order_anon_user.price_order = total_cost_order_anon_user
    order_anon_user.ordered_products = ordered_products
    order_anon_user.is_created = True

    db.commit()

    return order_anon_user


async def confirm_order(order_id: int, db: Session) -> Order | None:
    """Confirmation of user order by admin and changing order status"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order and order.confirmation_manager is False:
        order.confirmation_manager = True
        order.status_order = OrdersStatus.in_processing
        db.commit()
        return order
    return None


async def confirm_payment_of_order(order_id: int, db: Session) -> Order | None:
    """Confirmation of payment of order by admin or moderator"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order and order.confirmation_pay is False:
        order.confirmation_pay = True
        db.commit()
        return order
    return None


async def change_order_status(order_id: int, update_data: UpdateOrderStatus, db: Session) -> Order | None:
    """Change status of order by admin or moderator"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order:
        order.status_order = update_data.new_status
        db.commit()
        return order
    return None

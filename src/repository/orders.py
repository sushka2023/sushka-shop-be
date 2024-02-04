import logging

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
    AnonymousUser,
    BasketAnonUser,
)
from src.schemas.orders import (
    OrderModel,
    OrderAnonymUserNovaPoshtaWarehouseModel,
    OrderAnonymUserNovaPoshtaAddressModel,
    OrderAnonymUserUkrPoshtaModel,
)
from src.services.orders import (
    delete_basket_items_by_basket_id,
    delete_basket_items_by_basket_number_id,
    calculate_basket_total_cost,
    calculate_basket_total_cost_for_anonym_user,
    move_product_to_ordered,
    move_product_to_ordered_for_anon_user,
)
from src.repository import prices as repository_prices
from src.services.validation import validate_phone_number

logger = logging.getLogger(__name__)


async def get_order_by_id(order_id: int, db: Session) -> Order | None:
    return db.query(Order).filter_by(id=order_id).first()


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


async def get_anon_user_with_basket_and_items(
        user_anon_id: str, db: Session
) -> AnonymousUser:
    anon_user = (
        db.query(AnonymousUser)
        .options(
            joinedload(AnonymousUser.baskets)
            .joinedload(BasketAnonUser.basket_items_anon_user)
        )
        .filter(AnonymousUser.user_anon_id == user_anon_id)
        .first()
    )
    return anon_user


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
        is_authenticated=order_data.is_authenticated,
        ordered_products=ordered_products
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    await delete_basket_items_by_basket_id(user.basket.id, db)

    return order


async def create_order_anonym_user_with_nova_poshta_warehouse(
        order_data: OrderAnonymUserNovaPoshtaWarehouseModel, user_anon_id: str, db: Session
):
    """Create an order and clean the anonym user’s shopping cart after creating an order"""

    anon_user = await get_anon_user_with_basket_and_items(user_anon_id, db)

    if not anon_user.baskets:
        anon_user.baskets = BasketAnonUser()

    total_cost_order_anon_user = (
        await calculate_basket_total_cost_for_anonym_user(anon_user.baskets[0])
    )

    ordered_products = []
    for basket_item in anon_user.baskets[0].basket_items_anon_user:
        ordered_product = await move_product_to_ordered_for_anon_user(db, basket_item)

        selected_price = await repository_prices.price_by_product_id_and_price_id(
            ordered_product.product_id, ordered_product.price_id, db
        )

        if selected_price:
            ordered_product.prices = selected_price

        ordered_products.append(ordered_product)

    try:
        validate_phone_number(order_data.phone_number_anon_user)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    order_anonym_user = Order(
        anonymous_user_id=anon_user.id,
        basket_number_id=anon_user.baskets[0].id,
        first_name_anon_user=order_data.first_name_anon_user,
        last_name_anon_user=order_data.last_name_anon_user,
        email_anon_user=order_data.email_anon_user,
        phone_number_anon_user=order_data.phone_number_anon_user,
        post_type=order_data.post_type,
        country=order_data.country,
        city=order_data.city,
        address_warehouse=order_data.address_warehouse,
        price_order=total_cost_order_anon_user,
        payment_type=order_data.payment_type,
        call_manager=order_data.call_manager,
        is_authenticated=order_data.is_authenticated,
        ordered_products=ordered_products
    )

    db.add(order_anonym_user)
    db.commit()
    db.refresh(order_anonym_user)

    await delete_basket_items_by_basket_number_id(anon_user.baskets[0].id, db)

    return order_anonym_user


async def create_order_anonym_user_with_nova_poshta_address(
        order_data: OrderAnonymUserNovaPoshtaAddressModel, user_anon_id: str, db: Session
):
    """Create an order and clean the anonym user’s shopping cart after creating an order"""

    anon_user = await get_anon_user_with_basket_and_items(user_anon_id, db)

    if not anon_user.baskets:
        anon_user.baskets = BasketAnonUser()

    total_cost_order_anon_user = (
        await calculate_basket_total_cost_for_anonym_user(anon_user.baskets[0])
    )

    ordered_products = []
    for basket_item in anon_user.baskets[0].basket_items_anon_user:
        ordered_product = await move_product_to_ordered_for_anon_user(db, basket_item)

        selected_price = await repository_prices.price_by_product_id_and_price_id(
            ordered_product.product_id, ordered_product.price_id, db
        )

        if selected_price:
            ordered_product.prices = selected_price

        ordered_products.append(ordered_product)

    try:
        validate_phone_number(order_data.phone_number_anon_user)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    order_anonym_user = Order(
        anonymous_user_id=anon_user.id,
        basket_number_id=anon_user.baskets[0].id,
        first_name_anon_user=order_data.first_name_anon_user,
        last_name_anon_user=order_data.last_name_anon_user,
        email_anon_user=order_data.email_anon_user,
        phone_number_anon_user=order_data.phone_number_anon_user,
        post_type=order_data.post_type,
        country=order_data.country,
        city=order_data.city,
        area=order_data.area,
        region=order_data.region,
        street=order_data.street,
        house_number=order_data.house_number,
        apartment_number=order_data.apartment_number,
        floor=order_data.floor,
        price_order=total_cost_order_anon_user,
        payment_type=order_data.payment_type,
        call_manager=order_data.call_manager,
        is_authenticated=order_data.is_authenticated,
        ordered_products=ordered_products
    )

    db.add(order_anonym_user)
    db.commit()
    db.refresh(order_anonym_user)

    await delete_basket_items_by_basket_number_id(anon_user.baskets[0].id, db)

    return order_anonym_user


async def create_order_anonym_user_with_ukr_poshta(
        order_data: OrderAnonymUserUkrPoshtaModel, user_anon_id: str, db: Session
):
    """Create an order and clean the anonym user’s shopping cart after creating an order"""

    anon_user = await get_anon_user_with_basket_and_items(user_anon_id, db)

    if not anon_user.baskets:
        anon_user.baskets = BasketAnonUser()

    total_cost_order_anon_user = (
        await calculate_basket_total_cost_for_anonym_user(anon_user.baskets[0])
    )

    ordered_products = []
    for basket_item in anon_user.baskets[0].basket_items_anon_user:
        ordered_product = await move_product_to_ordered_for_anon_user(db, basket_item)

        selected_price = await repository_prices.price_by_product_id_and_price_id(
            ordered_product.product_id, ordered_product.price_id, db
        )

        if selected_price:
            ordered_product.prices = selected_price

        ordered_products.append(ordered_product)

    try:
        validate_phone_number(order_data.phone_number_anon_user)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    order_anonym_user = Order(
        anonymous_user_id=anon_user.id,
        basket_number_id=anon_user.baskets[0].id,
        first_name_anon_user=order_data.first_name_anon_user,
        last_name_anon_user=order_data.last_name_anon_user,
        email_anon_user=order_data.email_anon_user,
        phone_number_anon_user=order_data.phone_number_anon_user,
        post_type=order_data.post_type,
        country=order_data.country,
        city=order_data.city,
        area=order_data.area,
        region=order_data.region,
        street=order_data.street,
        house_number=order_data.house_number,
        apartment_number=order_data.apartment_number,
        floor=order_data.floor,
        post_code=order_data.post_code,
        price_order=total_cost_order_anon_user,
        payment_type=order_data.payment_type,
        call_manager=order_data.call_manager,
        is_authenticated=order_data.is_authenticated,
        ordered_products=ordered_products
    )

    db.add(order_anonym_user)
    db.commit()
    db.refresh(order_anonym_user)

    await delete_basket_items_by_basket_number_id(anon_user.baskets[0].id, db)

    return order_anonym_user


async def confirm_order(order_id: int, db: Session) -> Order | None:
    """Confirmation of user order by admin and changing order status"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order and order.confirmation_manager is False:
        order.confirmation_manager = True
        order.status_order = OrdersStatus.in_processing
        db.commit()
        return order
    return None

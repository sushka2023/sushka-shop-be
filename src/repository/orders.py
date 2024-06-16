import logging

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
    Price, PostType
)
from src.schemas.orders import (
    OrderModel,
    OrderAnonymUserModel,
    UpdateOrderStatus,
    OrderAdminNotesModel,
    OrdersCRMWithTotalCountResponse,
    OrdersCRMResponse,
    OrdersCurrentUserWithTotalCountResponse,
    OrderResponse,
)
from src.schemas.posts import PostNovaPoshtaOffice

from src.services.orders import (
    delete_basket_items_by_basket_id,
    calculate_basket_total_cost,
    calculate_basket_total_cost_for_anonym_user,
    move_product_to_ordered,
)
from src.repository import prices as repository_prices
from src.repository import products as repository_products
from src.repository import nova_poshta as repository_nova_poshta
from src.repository import ukr_poshta as repository_ukr_poshta
from src.repository import posts as repository_posts
from src.services.validation import validate_phone_number
from src.services.exception_detail import ExDetail as Ex

logger = logging.getLogger(__name__)


async def get_order_by_id(order_id: int, db: Session) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


async def get_order_by_id_for_current_user(
        order_id: int, user_id: int, db: Session
) -> Order | None:
    return db.query(Order).filter(
        Order.id == order_id,
        Order.is_authenticated,
        Order.user_id == user_id
    ).first()


async def get_orders_by_auth_user(
        limit: int, offset: int, user: User, db: Session
) -> OrdersCurrentUserWithTotalCountResponse | None:
    subquery = (
        db.query(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.ordered_products)
            .selectinload(OrderedProduct.prices)
            .options(
                joinedload(Price.product),
                joinedload(Price.ordered_products)
            ),
            selectinload(Order.selected_nova_poshta),
            selectinload(Order.selected_ukr_poshta)
        )
        .filter(OrderedProduct.order_id == Order.id)
        .filter(Price.id == OrderedProduct.price_id)
        .filter(Order.user_id == user.id)
        .order_by(desc(Order.created_at))
    )

    orders = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    orders_data = [OrderResponse(**order.__dict__) for order in orders]

    response_data = OrdersCurrentUserWithTotalCountResponse(
        orders=orders_data,
        total_count=total_count
    )

    return response_data


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
    try:
        if order_data.phone_number_current_user:
            validate_phone_number(order_data.phone_number_current_user)
        if order_data.phone_number_another_recipient:
            validate_phone_number(order_data.phone_number_another_recipient)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    user = await get_auth_user_with_basket_and_items(user_id, db)

    if not user.basket:
        user.basket = Basket()

    if not user.phone_number and not order_data.phone_number_current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to add a phone number in your account or provide one in the order!"
        )

    nova_poshta = None
    ukr_poshta = None
    selected_nova_poshta = None
    selected_ukr_poshta = None

    if order_data.selected_nova_poshta_id:
        nova_poshta = await repository_nova_poshta.get_nova_poshta_by_id(order_data.selected_nova_poshta_id, db)
        if not nova_poshta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nova Poshta not found")
        if nova_poshta.is_delivery:
            selected_nova_poshta = await repository_nova_poshta.get_nova_poshta_address_delivery(
                nova_poshta.id, user.id, db
            )
        else:
            selected_nova_poshta = await repository_nova_poshta.get_nova_poshta_warehouse(nova_poshta.id, user.id, db)
        if not selected_nova_poshta:
            nova_poshta_in = PostNovaPoshtaOffice(
                post_id=user.posts.id, nova_poshta_id=order_data.selected_nova_poshta_id
            )
            await repository_posts.add_nova_poshta_warehouse_to_post_for_current_user(db, nova_poshta_in, user_id)
            selected_nova_poshta = await repository_nova_poshta.get_nova_poshta_by_id(
                order_data.selected_nova_poshta_id, db
            )

    if order_data.selected_ukr_poshta_id:
        ukr_poshta = await repository_ukr_poshta.get_ukr_poshta_by_id(order_data.selected_ukr_poshta_id, db)
        if not ukr_poshta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ukr Poshta not found")
        selected_ukr_poshta = await repository_ukr_poshta.get_ukr_poshta_address_delivery(ukr_poshta.id, user.id, db)
        if not selected_ukr_poshta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ukr Poshta address not found")

    if not nova_poshta and not ukr_poshta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid delivery method selected")

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

    if len(ordered_products) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your shopping cart is still empty. Order cannot be without products"
        )

    order = Order(
        user_id=user.id,
        user=user,
        is_another_recipient=order_data.is_another_recipient,
        full_name_another_recipient=order_data.full_name_another_recipient,
        phone_number_another_recipient=order_data.phone_number_another_recipient,
        basket_id=user.basket.id,
        price_order=total_cost,
        payment_type=order_data.payment_type,
        call_manager=order_data.call_manager,
        selected_nova_poshta_id=order_data.selected_nova_poshta_id,
        selected_nova_poshta=selected_nova_poshta,
        selected_ukr_poshta_id=order_data.selected_ukr_poshta_id,
        selected_ukr_poshta=selected_ukr_poshta,
        ordered_products=ordered_products,
        comment=order_data.comment
    )

    if nova_poshta and nova_poshta.is_delivery:
        order.post_type = PostType.nova_poshta_address
    elif nova_poshta and not nova_poshta.is_delivery:
        order.post_type = PostType.nova_poshta_warehouse
    elif ukr_poshta:
        order.post_type = PostType.ukr_poshta

    order.is_authenticated = True

    try:
        db.add(order)
        db.commit()
        db.refresh(order)

        if order_data.phone_number_current_user:
            user.phone_number = order_data.phone_number_current_user
            db.commit()

        await delete_basket_items_by_basket_id(user.basket.id, db)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create order: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")

    return order


async def create_order_anonym_user(data: OrderAnonymUserModel, db: Session):
    """Create an order of the anonym user"""

    try:
        validate_phone_number(data.phone_number_anon_user)
        validate_phone_number(data.phone_number_another_recipient)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    order_data = data.dict()
    ordered_products_data = order_data.pop("ordered_products", [])

    for product_data in ordered_products_data:
        product_id = product_data.get("product_id")
        price_id = product_data.get("price_id")
        quantity = product_data.get("quantity", 0)

        product = await repository_products.product_by_id_and_status(product_id=product_id, db=db)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

        prise = await repository_prices.price_by_product_id_and_price_id(product_id, price_id, db)

        if not prise:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid quantity. Product quantity must be greater than 0"
            )

    order = Order(**order_data)

    db.add(order)
    db.commit()
    db.refresh(order)

    for product_data in ordered_products_data:
        product = OrderedProduct(
            product_id=product_data.get("product_id"),
            price_id=product_data.get("price_id"),
            quantity=product_data.get("quantity"),
            order_id=order.id
        )
        db.add(product)

    db.commit()

    total_cost_order = await calculate_basket_total_cost_for_anonym_user(order.id, db)

    order.price_order = total_cost_order
    db.commit()

    return order


async def confirm_payment_of_order(order_id: int, db: Session) -> Order | None:
    """Confirmation of payment of order by admin or moderator"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order and order.confirmation_pay is False:
        order.confirmation_pay = True
        db.commit()
        return order
    return None


async def change_order_status(
        order_id: int, update_data: UpdateOrderStatus, db: Session
) -> Order | None:
    """Change status of order by admin or moderator"""

    order = await get_order_by_id(order_id=order_id, db=db)
    if order:
        order.status_order = update_data.new_status
        order.confirmation_manager = True
        db.commit()
        return order
    return None


async def get_orders_all_for_crm(
        limit: int, offset: int, order_status: OrdersStatus,  db: Session
) -> OrdersCRMWithTotalCountResponse | None:
    subquery = (
        db.query(Order)
        .options(
            selectinload(Order.ordered_products)
            .selectinload(OrderedProduct.prices)
            .options(
                joinedload(Price.product),
                joinedload(Price.ordered_products)
            ),
            selectinload(Order.selected_nova_poshta),
            selectinload(Order.selected_ukr_poshta)
        )
        .filter(OrderedProduct.order_id == Order.id)
        .filter(Price.id == OrderedProduct.price_id)
        .order_by(Order.status_order, desc(Order.created_at))
    )

    if order_status:
        subquery = subquery.filter(Order.status_order == order_status)

    orders = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    orders_data = [OrdersCRMResponse(**order.__dict__) for order in orders]

    response_data = OrdersCRMWithTotalCountResponse(
        orders=orders_data,
        total_count=total_count
    )

    return response_data


async def add_notes_to_order(order_id: int, body: OrderAdminNotesModel, db: Session):
    order = await get_order_by_id(order_id=order_id, db=db)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    order.notes_admin = body.notes
    db.commit()
    return order

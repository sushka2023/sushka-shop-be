import pickle

from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role, User
from src.repository import orders as repository_orders
from src.schemas.orders import (
    OrderResponse,
    OrderModel,
    OrderConfirmModel,
    OrderAnonymUserNovaPoshtaWarehouseModel,
    OrderAnonymUserNovaPoshtaAddressModel,
    OrderAnonymUserUkrPoshtaModel,
    OrderAnonymUserNovaPoshtaWarehouseResponse,
    OrderAnonymUserNovaPoshtaAddressResponse,
    OrderAnonymUserUkrPoshtaResponse,
    OrderAnonymUserResponse,
    OrderMessageResponse
)
from src.services.auth import auth_service
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex


router = APIRouter(prefix="/orders", tags=["orders"])


allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get(
    "/for_current_user", response_model=list[OrderResponse],
    dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def get_orders_current_user(
        limit: int,
        offset: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    The function returns a list of all orders in the database which were created by a current user.

    Args:
        limit: int: Limit the number of orders returned
        offset: int: Specify the offset of the first order to be returned
        current_user (User): the current user who created the orders'
        db: Session: Access the database

    Returns:
        A list of orders
    """
    redis_client = get_redis()

    key = f"orders_user:{current_user.id}_limit:{limit}_offset:{offset}"

    cached_orders = None

    if redis_client:
        cached_orders = redis_client.get(key)

    if not cached_orders:
        orders = await repository_orders.get_orders_by_auth_user(limit, offset, current_user, db)

        if redis_client:
            redis_client.set(key, pickle.dumps(orders))
            redis_client.expire(key, 1800)
    else:
        orders = pickle.loads(cached_orders)

    return orders


@router.get("/all_auth_users_for_crm", response_model=list[OrderResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_orders_auth_users_for_crm(limit: int, offset: int, db: Session = Depends(get_db)):
    """
    The function returns a list of all orders in the database.

    Args:
        limit: int: Limit the number of orders returned
        offset: int: Specify the offset of the first order to be returned
        db: Session: Access the database

    Returns:
        A list of orders
    """
    return await repository_orders.get_orders_auth_user_for_crm(limit, offset, db)


@router.get("/all_anonym_users_for_crm", response_model=list[OrderAnonymUserResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_orders_anonym_users_for_crm(limit: int, offset: int, db: Session = Depends(get_db)):
    """
    The function returns a list of all orders in the database.

    Args:
        limit: int: Limit the number of orders returned
        offset: int: Specify the offset of the first order to be returned
        db: Session: Access the database

    Returns:
        A list of orders
    """
    return await repository_orders.get_orders_anonym_user_for_crm(limit, offset, db)


@router.post("/create_for_auth_user",
             response_model=OrderResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def create_order_auth_user(
        order_data: OrderModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
        The create of order function creates a new order in the database.

        Args:
            order_data: OrderModel: Validate the request body
            db: Session: Pass the database session to the repository layer
            current_user (User): the current user attempting to create the order

        Returns:
            An order object
        """

    new_order = await repository_orders.create_order_auth_user(order_data, current_user.id, db)

    await delete_cache_in_redis()

    return new_order


@router.post("/create_for_anonym_user_with_nova_poshta_warehouse",
             response_model=OrderAnonymUserNovaPoshtaWarehouseResponse,
             status_code=status.HTTP_201_CREATED)
async def create_order_anonym_user_with_nova_poshta_warehouse(
        order_data: OrderAnonymUserNovaPoshtaWarehouseModel,
        user_anon_id: str = Header(...),
        db: Session = Depends(get_db),
):
    """
        The create of order function creates a new order in the database.

        Args:
            order_data: OrderAnonymUserNovaPoshtaWarehouseModel: Validate the request body
            db: Session: Pass the database session to the repository layer
            user_anon_id: AnonymousUser: unique identity data of anonym user

        Returns:
            An order object
        """

    new_order_anonym_user = (
        await repository_orders.create_order_anonym_user_with_nova_poshta_warehouse(
            order_data, user_anon_id, db
        )
    )

    return new_order_anonym_user


@router.post("/create_for_anonym_user_with_nova_poshta_address",
             response_model=OrderAnonymUserNovaPoshtaAddressResponse,
             status_code=status.HTTP_201_CREATED)
async def create_order_anonym_user_with_nova_poshta_address(
        order_data: OrderAnonymUserNovaPoshtaAddressModel,
        user_anon_id: str = Header(...),
        db: Session = Depends(get_db),
):
    """
        The create of order function creates a new order in the database.

        Args:
            order_data: OrderAnonymUserNovaPoshtaAddressModel: Validate the request body
            db: Session: Pass the database session to the repository layer
            user_anon_id: AnonymousUser: unique identity data of anonym user

        Returns:
            An order object
        """

    new_order_anonym_user = (
        await repository_orders.create_order_anonym_user_with_nova_poshta_address(
            order_data, user_anon_id, db
        )
    )

    return new_order_anonym_user


@router.post("/create_for_anonym_user_with_ukr_poshta",
             response_model=OrderAnonymUserUkrPoshtaResponse,
             status_code=status.HTTP_201_CREATED)
async def create_order_anonym_user_with_ukr_poshta(
        order_data: OrderAnonymUserUkrPoshtaModel,
        user_anon_id: str = Header(...),
        db: Session = Depends(get_db),
):
    """
        The create of order function creates a new order in the database.

        Args:
            order_data: OrderAnonymUserUkrPoshtaModel: Validate the request body
            db: Session: Pass the database session to the repository layer
            user_anon_id: AnonymousUser: unique identity data of anonym user

        Returns:
            An order object
        """

    new_order_anonym_user = (
        await repository_orders.create_order_anonym_user_with_ukr_poshta(
            order_data, user_anon_id, db
        )
    )

    return new_order_anonym_user


@router.put("/confirm_order",
            response_model=OrderMessageResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def confirm_order(order: OrderConfirmModel, db: Session = Depends(get_db)):
    """
    The confirm_order function confirms an order.

    Args:
        order: OrderConfirmModel: Get the id of the order to confirm and changed status of field confirmation_manager
        db: Session: Access the database

    Returns:
        Message that the order was confirmed successfully
    """
    order = await repository_orders.get_order_by_id(order.id, db)

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if order.confirmation_manager:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    await repository_orders.confirm_order(order.id, db)

    await delete_cache_in_redis()

    return {"message": "Order confirmed successfully"}

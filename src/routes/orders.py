import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role, User
from src.repository import orders as repository_orders
from src.schemas.orders import OrderResponse, OrderModel, OrderConfirmModel
from src.services.auth import auth_service
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex


router = APIRouter(prefix="/orders", tags=["orders"])


allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get(
    "/", response_model=list[OrderResponse],
    dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def get_orders(
        limit: int,
        offset: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
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
        orders = await repository_orders.get_orders_by_user(limit, offset, current_user, db)

        if redis_client:
            redis_client.set(key, pickle.dumps(orders))
            redis_client.expire(key, 1800)
    else:
        orders = pickle.loads(cached_orders)

    return orders


@router.get("/all_for_crm", response_model=list[OrderResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_orders_for_crm(limit: int, offset: int, db: Session = Depends(get_db)):
    """
    The function returns a list of all orders in the database.

    Args:
        limit: int: Limit the number of orders returned
        offset: int: Specify the offset of the first order to be returned
        db: Session: Access the database

    Returns:
        A list of orders
    """
    return await repository_orders.get_orders_for_crm(limit, offset, db)


@router.post("/create",
             response_model=OrderResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def create_order(
        order_data: OrderModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db),
):
    """
        The create_order function creates a new order in the database.

        Args:
            order_data: OrderModel: Validate the request body
            db: Session: Pass the database session to the repository layer
            current_user (User): the current user attempting to create the order

        Returns:
            An order object
        """

    new_order = await repository_orders.create_order(order_data, current_user.id, db)

    await delete_cache_in_redis()

    return new_order


@router.put("/confirm_order",
            response_model=OrderResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def confirm_order(order: OrderConfirmModel, db: Session = Depends(get_db)):
    """
    The confirm_order function confirms an order.

    Args:
        order: OrderConfirmModel: Get the id of the order to confirm and changed status of field confirmation_manager
        db: Session: Access the database

    Returns:
        An order confirmed model object
    """
    order = await repository_orders.get_order_by_id(order.id, db)

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if order.confirmation_manager:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    confirmed_order = await repository_orders.confirm_order(order.id, db)

    await delete_cache_in_redis()

    return confirmed_order

import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role, User, OrdersStatus
from src.repository import orders as repository_orders
from src.schemas.orders import (
    OrderResponse,
    OrderModel,
    OrderConfirmModel,
    OrderAnonymUserResponse,
    OrderMessageResponse,
    OrderAnonymUserModel,
    UpdateOrderStatus,
    OrdersCRMResponse,
    OrderCommentModel,
)

from src.services.auth import auth_service
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex


router = APIRouter(prefix="/orders", tags=["orders"])


allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


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


@router.post("/create_for_anonym_user",
             response_model=OrderAnonymUserResponse,
             status_code=status.HTTP_201_CREATED)
async def create_order_anonym_user(
        order_data: OrderAnonymUserModel,
        db: Session = Depends(get_db),
):
    """
    The create of order function creates a new order in the database.

    Args:
        order_data: OrderAnonymUserModel: Validate the request body
        db: Session: Pass the database session to the repository layer

    Returns:
        An order object
    """

    new_order_anonym_user = (
        await repository_orders.create_order_anonym_user(order_data, db)
    )

    await delete_cache_in_redis()

    return new_order_anonym_user


@router.get("/all_for_crm",
            response_model=list[OrdersCRMResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_orders_for_crm(
        limit: int, offset: int, order_status: OrdersStatus = None, db: Session = Depends(get_db)
):

    """
    The orders_for_crm function returns a list of orders for the CRM.

    :param limit: int: Limit the number of orders returned
    :param offset: int: Indicate the number of records to skip
    :param order_status: OrdersStatus: Filter orders by status
    :param db: Session: Pass the database connection to the function

    :return: A list of orders
    """
    redis_client = get_redis()

    key = f"orders:order_status_{order_status}_limit:{limit}_offset:{offset}"

    cached_orders = None

    if redis_client:
        cached_orders = redis_client.get(key)

    orders_ = None

    if not cached_orders:
        if not order_status:
            orders_ = await repository_orders.get_orders_all_for_crm(limit, offset, db)
        elif order_status:
            orders_ = await repository_orders.get_orders_all_for_crm_with_status(limit, offset, order_status, db)

        if redis_client:
            redis_client.set(key, pickle.dumps(orders_))
            redis_client.expire(key, 1800)

    else:
        orders_ = pickle.loads(cached_orders)

    if not orders_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return orders_


@router.get("/{order_id}/for_crm",
            response_model=OrdersCRMResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_order_by_id_for_crm(
        order_id: int, db: Session = Depends(get_db)
):
    """
    The get_order_by_id_for_crm function returns an order by id for the CRM.

    :param order_id: Get the id of the order
    :param db: Session: Pass the database connection to the function

    :return: An order
    """
    order = await repository_orders.get_order_by_id(order_id, db)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return order


@router.get("/for_current_user",
            response_model=list[OrderResponse],
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


@router.get("/{order_id}/for_current_user",
            response_model=OrderResponse,
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def get_order_by_id_for_current_user(
        order_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    The function returns an order in the database which was created by a current user.

    Args:
        order_id: Get the id of the order of current user
        current_user (User): the current user who created the orders'
        db: Session: Access the database

    Returns:
        An order
    """
    order = await repository_orders.get_order_by_id_for_current_user(order_id, current_user.id, db)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return order


@router.put("/confirm_payment_of_order",
            response_model=OrderMessageResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def confirm_payment_of_order(order_data: OrderConfirmModel, db: Session = Depends(get_db)):
    """
    The confirm_payment_of_order function confirms a payment of order.

    Args:
        order_data: OrderConfirmModel: Get the id of the order to confirm the payment of the orders'
        db: Session: Access the database

    Returns:
        Message that the payment of the order was confirmed successfully
    """
    order = await repository_orders.get_order_by_id(order_data.id, db)

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if order.confirmation_pay:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    await repository_orders.confirm_payment_of_order(order.id, db)

    await delete_cache_in_redis()

    return {"message": "Payment of Order confirmed successfully"}


@router.put("/{order_id}/update_status",
            response_model=OrderMessageResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def change_order_status(order_id: int, update_data: UpdateOrderStatus, db: Session = Depends(get_db)):
    """
    The change_order_status function changes an order status.

    Args:
        update_data: UpdateOrderStatus: the order status to be changed
        order_id: Get the id of the order to change it status
        db: Session: Access the database

    Returns:
        Message that the status of the order was changed successfully
    """
    order = await repository_orders.get_order_by_id(order_id, db)

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    await repository_orders.change_order_status(order.id, update_data, db)

    await delete_cache_in_redis()

    return {"message": f"Status of the Order №{order_id} updated to '{update_data.new_status.value}'"}


@router.put("/{order_id}/add_comment",
            response_model=OrderMessageResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def add_comment_to_order(order_id: int, data: OrderCommentModel, db: Session = Depends(get_db)):
    """
    The add_comment_to_order function adds comment to the order.

    Args:
        data: OrderCommentModel: adding comment to the order by admin or moderator
        order_id: Get the id of the order to add comment
        db: Session: Access the database

    Returns:
        Message that the comment to the order was added successfully
    """

    await repository_orders.add_comment_to_order(order_id, data, db)

    await delete_cache_in_redis()

    return {"message": f"Comment to the Order №{order_id} added successfully"}

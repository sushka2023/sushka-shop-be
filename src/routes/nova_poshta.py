import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role
from src.repository import nova_poshta as repository_novaposhta
from src.schemas.nova_poshta import (
    NovaPoshtaAddressDeliveryResponse,
    NovaPoshtaAddressDeliveryCreate,
    NovaPoshtaResponse,
    NovaPoshtaCreate,
    NovaPoshtaAddressDeliveryPartialUpdate,
    NovaPoshtaDataResponse
)
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/nova_poshta", tags=["novaposhta offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/",
            response_model=list[NovaPoshtaDataResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def get_all_nova_postal_warehouse(db: Session = Depends(get_db)):
    """
    The function returns a list of all nova postal warehouse in the database.

    Args:
        db: Session: Access the database

    Returns:
        A list of nova postal objects
    """
    redis_client = get_redis()

    key = f"novaposhta"

    cached_novaposhta = None

    if redis_client:
        cached_novaposhta = redis_client.get(key)

    if not cached_novaposhta:
        novaposhta_data = await repository_novaposhta.get_all_nova_poshta_data(db)

        if novaposhta_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND
            )

        if redis_client:
            redis_client.set(key, pickle.dumps(novaposhta_data))
            redis_client.expire(key, 1800)
    else:
        novaposhta_data = pickle.loads(cached_novaposhta)

    return novaposhta_data


@router.post("/create_address_delivery",
             response_model=NovaPoshtaAddressDeliveryResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create_nova_poshta_address_delivery(nova_postal_address_delivery: NovaPoshtaAddressDeliveryCreate,
                                              db: Session = Depends(get_db)):
    """
    The create function creates a new novaposhta with address delivery.

    Args:
        nova_postal_address_delivery: NovaPoshtaAddressDeliveryCreate: Validate the request body
        db: Session: Access the database

    Returns:
        An novaposhta object
    """
    new_nova_poshta_address_delivery = (
        await repository_novaposhta.create_nova_poshta_address_delivery(nova_postal_address_delivery, db)
    )

    await delete_cache_in_redis()

    return new_nova_poshta_address_delivery


@router.post("/create_warehouse",
             response_model=NovaPoshtaResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create_nova_poshta_warehouse(nova_postal_warehouse: NovaPoshtaCreate,
                                       db: Session = Depends(get_db)):
    """
    The create function creates a new novaposhta warehouse.

    Args:
        nova_postal_warehouse: NovaPoshtaCreate: Validate the request body
        db: Session: Access the database

    Returns:
        An novaposhta object
    """
    new_nova_poshta_warehouse = (
        await repository_novaposhta.create_nova_poshta_warehouse(nova_postal_warehouse, db)
    )

    await delete_cache_in_redis()

    return new_nova_poshta_warehouse


@router.patch("/{nova_poshta_id}/partial-update",
              dependencies=[Depends(allowed_operation_admin_moderator_user)],
              response_model=NovaPoshtaAddressDeliveryResponse)
async def update_nova_poshta_data(
    nova_poshta_id: int,
    nova_poshta_data: NovaPoshtaAddressDeliveryPartialUpdate,
    db: Session = Depends(get_db)
):
    """
    Change the novaposhta data

    Arguments:
        nova_poshta_id: int
        nova_poshta_data: NovaPoshtaAddressDeliveryPartialUpdate: object with updated novaposhta data
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        NovaPoshta: object after the change operation
    """
    update_data = {
        key: value
        for key, value in nova_poshta_data.model_dump().items()
        if value is not None
    }

    updated_novaposhta_data = await repository_novaposhta.update_nova_poshta_data(db, nova_poshta_id, update_data)

    await delete_cache_in_redis()

    return updated_novaposhta_data

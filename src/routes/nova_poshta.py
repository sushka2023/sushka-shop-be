from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import nova_poshta as repository_novaposhta
from src.schemas.nova_poshta import (
    NovaPoshtaAddressDeliveryResponse,
    NovaPoshtaAddressDeliveryPartialUpdate,
)
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess


router = APIRouter(prefix="/nova_poshta", tags=["novaposhta offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


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
        for key, value in nova_poshta_data.dict().items()
        if value is not None
    }

    updated_novaposhta_data = (
        await repository_novaposhta.update_nova_poshta_data(db, nova_poshta_id, update_data)
    )

    await delete_cache_in_redis()

    return updated_novaposhta_data

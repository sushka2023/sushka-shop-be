from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import ukr_poshta as repository_ukrposhta
from src.services.cache_in_redis import delete_cache_in_redis

from src.schemas.ukr_poshta import UkrPoshtaResponse, UkrPoshtaPartialUpdate
from src.services.roles import RoleAccess


router = APIRouter(prefix="/ukr_poshta", tags=["ukrposhta offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.patch("/{ukr_poshta_id}/partial-update",
              dependencies=[Depends(allowed_operation_admin_moderator_user)],
              response_model=UkrPoshtaResponse)
async def update_ukr_poshta_data(
    ukr_poshta_id: int,
    ukr_poshta_data: UkrPoshtaPartialUpdate,
    db: Session = Depends(get_db)
):
    """
    Change the ukrposhta data

    Arguments:
        ukr_poshta_id: int
        ukr_poshta_data: UkrPoshtaForm: object with updated ukrposhta data
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        UkrPoshta: object after the change operation
    """
    update_data = {
        key: value
        for key, value in ukr_poshta_data.model_dump().items()
        if value is not None
    }

    updated_ukrposhta_data = (
        await repository_ukrposhta.update_ukr_poshta_data(db, ukr_poshta_id, update_data)
    )

    await delete_cache_in_redis()

    return updated_ukrposhta_data

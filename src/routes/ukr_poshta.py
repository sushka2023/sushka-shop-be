from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import ukr_poshta as repository_ukrposhta

from src.schemas.ukr_poshta import UkrPoshtaResponse, UkrPoshtaCreate
from src.services.roles import RoleAccess


router = APIRouter(prefix="/ukr_poshta", tags=["ukrposhta offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post("/create",
             response_model=UkrPoshtaResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create_ukr_poshta_office(ukr_postal_office: UkrPoshtaCreate,
                                   db: Session = Depends(get_db)):
    """
    The create function creates a new ukrposhta office.

    Args:
        ukr_postal_office: UkrPoshtaCreate: Validate the request body
        db: Session: Access the database

    Returns:
        An ukrposhta object
    """
    return await repository_ukrposhta.create_ukr_poshta_office(ukr_postal_office, db)

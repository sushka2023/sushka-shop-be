from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import ukr_poshta as repository_ukrposhta

from src.schemas.ukr_poshta import UkrPoshtaResponse, UkrPoshtaCreate, UkrPoshtaPartialUpdate
from src.services.roles import RoleAccess


router = APIRouter(prefix="/ukr_poshta", tags=["ukrposhta offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/",
            response_model=list[UkrPoshtaResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def get_all_ukr_postal_offices(db: Session = Depends(get_db)):
    """
    The function returns a list of all ukr postal offices in the database.

    Args:
        db: Session: Access the database

    Returns:
        A list of ukr postal offices
    """
    return await repository_ukrposhta.get_ukr_poshta(db)


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

    return await repository_ukrposhta.update_ukr_poshta_data(db, ukr_poshta_id, update_data)

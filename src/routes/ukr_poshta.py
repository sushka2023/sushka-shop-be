import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role
from src.repository import ukr_poshta as repository_ukrposhta
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.exception_detail import ExDetail as Ex

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
    redis_client = get_redis()

    key = f"ukrposhta"

    cached_ukrposhta = None

    if redis_client:
        cached_ukrposhta = redis_client.get(key)

    if not cached_ukrposhta:
        ukrposhta_data = await repository_ukrposhta.get_ukr_poshta(db)

        if ukrposhta_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND
            )

        if redis_client:
            redis_client.set(key, pickle.dumps(ukrposhta_data))
            redis_client.expire(key, 1800)
    else:
        ukrposhta_data = pickle.loads(cached_ukrposhta)

    return ukrposhta_data


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
    new_ukr_poshta_office = await repository_ukrposhta.create_ukr_poshta_office(ukr_postal_office, db)

    await delete_cache_in_redis()

    return new_ukr_poshta_office


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

    updated_ukrposhta_data = await repository_ukrposhta.update_ukr_poshta_data(db, ukr_poshta_id, update_data)

    await delete_cache_in_redis()

    return updated_ukrposhta_data

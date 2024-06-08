from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import nova_poshta as repository_novaposhta
from src.schemas.nova_poshta import (
    NovaPoshtaAddressDeliveryResponse,
    NovaPoshtaAddressDeliveryPartialUpdate,
    NovaPoshtaMessageResponse,
)
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess


router = APIRouter(prefix="/nova_poshta", tags=["novaposhta offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/warehouses/{city}", response_model=list[str])
async def get_warehouses_for_city(city_with_area: str, db: Session = Depends(get_db)) -> list[str]:
    """
    Obtain the novaposhta data from API Nova Poshta and add received data to database

        Arguments:
            city_with_area: str: parameter to receive all warehouses for the specific data
            (the city or (the city and the area))
            db (Session): SQLAlchemy session object for accessing the database

    Returns:
        List of all warehouses for the specific city
    """
    return await repository_novaposhta.get_warehouses_data_for_specific_city(db=db, city_with_area=city_with_area)


@router.put("/update_warehouses",
            response_model=NovaPoshtaMessageResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def update_warehouses_data(db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Update the novaposhta data from API Nova Poshta in database

        Arguments:
            db (Session): SQLAlchemy session object for accessing the database

    Returns:
        Message about successfully updating novaposhta data
    """
    warehouses = await repository_novaposhta.get_all_warehouses(db=db)
    if not warehouses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Warehouses do not exist in the database"
        )

    await repository_novaposhta.update_warehouses_data(db=db)

    return {"message": "Warehouses data updated successfully."}


@router.delete("/delete_warehouses",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin)])
async def remove_warehouses_data(db: Session = Depends(get_db)) -> None:
    """
    Remove novaposhta data from database.

        Args:
            db: Session: Access the database

    Returns:
        None
    """
    await repository_novaposhta.delete_all_warehouses(db=db)


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

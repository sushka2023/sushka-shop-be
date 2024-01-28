from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import NovaPoshta
from src.schemas.nova_poshta import NovaPoshtaAddressDeliveryCreate, NovaPoshtaCreate
from src.services.exception_detail import ExDetail as Ex


async def create_nova_poshta_address_delivery(
        nova_post_address_delivery: NovaPoshtaAddressDeliveryCreate,
        db: Session,
) -> NovaPoshta:
    new_nova_poshta_address_delivery = NovaPoshta(**nova_post_address_delivery.dict)
    db.add(new_nova_poshta_address_delivery)
    db.commit()
    db.refresh(new_nova_poshta_address_delivery)
    return new_nova_poshta_address_delivery


async def create_nova_poshta_warehouse(
        nova_post_warehouse: NovaPoshtaCreate,
        db: Session,
) -> NovaPoshta:
    new_nova_poshta_warehouse = NovaPoshta(**nova_post_warehouse.dict())
    db.add(new_nova_poshta_warehouse)
    db.commit()
    db.refresh(new_nova_poshta_warehouse)
    return new_nova_poshta_warehouse


async def get_nova_poshta_by_id(nova_poshta_id: int, db: Session) -> NovaPoshta | None:
    return db.query(NovaPoshta).filter_by(id=nova_poshta_id).first()


async def update_nova_poshta_data(
    db: Session, nova_poshta_id: int, nova_poshta_data: dict
) -> NovaPoshta:

    updated_data_nova_poshta = await get_nova_poshta_by_id(nova_poshta_id=nova_poshta_id, db=db)

    if not updated_data_nova_poshta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if updated_data_nova_poshta.address_warehouse:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)

    updated_data_nova_poshta.update_from_dict(nova_poshta_data)

    db.commit()
    db.refresh(updated_data_nova_poshta)

    return updated_data_nova_poshta

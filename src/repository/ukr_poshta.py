from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from src.database.models import UkrPoshta
from src.schemas.ukr_poshta import UkrPoshtaCreate
from src.services.exception_detail import ExDetail as Ex


async def create_ukr_poshta_office(ukr_postal_office: UkrPoshtaCreate, db: Session) -> UkrPoshta:
    new_ukr_poshta_office = UkrPoshta(**ukr_postal_office.model_dump())
    db.add(new_ukr_poshta_office)
    db.commit()
    db.refresh(new_ukr_poshta_office)
    return new_ukr_poshta_office


async def get_ukr_poshta_by_id(ukr_poshta_id: int, db: Session) -> UkrPoshta | None:
    return db.query(UkrPoshta).filter_by(id=ukr_poshta_id).first()


async def update_ukr_poshta_data(
    db: Session, ukr_poshta_id: int, ukr_poshta_data: dict
) -> UkrPoshta:

    updated_data_ukr_poshta = await get_ukr_poshta_by_id(ukr_poshta_id=ukr_poshta_id, db=db)

    if not updated_data_ukr_poshta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    updated_data_ukr_poshta.update_from_dict(ukr_poshta_data)

    db.commit()
    db.refresh(updated_data_ukr_poshta)

    return updated_data_ukr_poshta

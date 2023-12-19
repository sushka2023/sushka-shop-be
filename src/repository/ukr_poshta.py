from sqlalchemy.orm import Session


from src.database.models import UkrPoshta
from src.schemas.ukr_poshta import UkrPoshtaCreate


async def create_ukr_poshta_office(ukr_postal_office: UkrPoshtaCreate, db: Session):
    new_ukr_poshta_office = UkrPoshta(**ukr_postal_office.model_dump())
    db.add(new_ukr_poshta_office)
    db.commit()
    db.refresh(new_ukr_poshta_office)
    return new_ukr_poshta_office


async def get_ukr_poshta_by_id(ukr_poshta_id: int, db: Session):
    return db.query(UkrPoshta).filter_by(id=ukr_poshta_id).first()

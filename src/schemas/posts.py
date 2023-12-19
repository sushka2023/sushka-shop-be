from typing import Optional

from pydantic import BaseModel

from src.schemas.ukr_poshta import UkrPoshtaResponse


class PostModel(BaseModel):
    user_id: int


class PostResponse(BaseModel):
    id: int
    user_id: int
    ukr_poshta_id: Optional[int] = None
    ukr_poshta: Optional[UkrPoshtaResponse] = []
    nova_poshta_id: Optional[int] = None

    class Config:
        orm_mode = True


class PostAddUkrPostalOffice(BaseModel):
    ukr_poshta_id: Optional[int] = None


class PostAddNovaPoshtaOffice(BaseModel):
    nova_poshta_id: Optional[int] = None

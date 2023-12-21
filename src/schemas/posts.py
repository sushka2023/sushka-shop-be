from typing import Optional

from pydantic import BaseModel

from src.schemas.ukr_poshta import UkrPoshtaResponse
from src.schemas.users import UserResponseForCRM


class PostModel(BaseModel):
    user_id: int


class PostResponse(BaseModel):
    id: int
    user_id: int
    user: Optional[UserResponseForCRM] = []
    ukr_poshta: Optional[list[UkrPoshtaResponse]] = []

    class Config:
        orm_mode = True


class PostUkrPostalOffice(BaseModel):
    post_id: int
    ukr_poshta_id: Optional[int] = None


class PostNovaPoshtaOffice(BaseModel):
    post_id: int
    nova_poshta_id: Optional[int] = None


class PostMessageResponse(BaseModel):
    message: str

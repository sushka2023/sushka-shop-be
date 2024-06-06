from typing import Optional

from pydantic import BaseModel

from src.schemas.nova_poshta import (
    NovaPoshtaDataResponse, NovaPoshtaResponse, NovaPoshtaAddressDeliveryResponse
)
from src.schemas.ukr_poshta import UkrPoshtaResponse
from src.schemas.users import UserResponseForOrder


class PostModel(BaseModel):
    user_id: int


class PostResponse(BaseModel):
    id: int
    user_id: int
    user: Optional[UserResponseForOrder] = []
    ukr_poshta: Optional[list[UkrPoshtaResponse]] = []
    nova_poshta: Optional[list[NovaPoshtaDataResponse]] = []

    class Config:
        orm_mode = True


class PostUkrPostalOffice(BaseModel):
    ukr_poshta_id: Optional[int] = None


class PostNovaPoshtaOffice(BaseModel):
    post_id: int
    nova_poshta_id: Optional[int] = None


class PostWarehouseResponse(BaseModel):
    message: str
    nova_poshta_data: NovaPoshtaResponse


class PostAddressDeliveryResponse(BaseModel):
    message: str
    nova_poshta_data: NovaPoshtaAddressDeliveryResponse


class PostUkrPoshtaResponse(BaseModel):
    message: str
    ukr_poshta_data: UkrPoshtaResponse


class PostMessageResponse(BaseModel):
    message: str

from typing import Optional

from pydantic import BaseModel


class NovaPoshtaAddressDeliveryModel(BaseModel):
    street: str
    house_number: str
    apartment_number: Optional[str] = ""
    floor: Optional[int] = None
    city: str
    region: Optional[str] = ""
    area: Optional[str] = ""


class NovaPoshtaAddressDeliveryCreate(NovaPoshtaAddressDeliveryModel):
    pass


class NovaPoshtaAddressDeliveryPartialUpdate(BaseModel):
    street: str | None = None
    house_number: str | None = None
    apartment_number: str | None = None
    floor: int | None = None
    city: str | None = None
    region: str | None = None
    area: str | None = None


class NovaPoshtaAddressDeliveryResponse(NovaPoshtaAddressDeliveryModel):
    id: int

    class Config:
        orm_mode = True


class NovaPoshtaModel(BaseModel):
    city: str
    address_warehouse: str


class NovaPoshtaCreate(NovaPoshtaModel):
    pass


class NovaPoshtaResponse(NovaPoshtaModel):
    id: int

    class Config:
        orm_mode = True


class NovaPoshtaDataResponse(BaseModel):
    id: int
    address_warehouse: Optional[str] = ""
    city: str
    region: Optional[str] = ""
    area: Optional[str] = ""
    street: Optional[str] = ""
    house_number: Optional[str] = ""
    apartment_number: Optional[str] = ""
    floor: Optional[int] = None

    class Config:
        orm_mode = True


class NovaPoshtaMessageResponse(BaseModel):
    message: str


class NovaPoshtaWarehouseResponse(BaseModel):
    id: int
    address_warehouse: str

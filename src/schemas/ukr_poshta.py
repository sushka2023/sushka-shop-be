from typing import Optional

from pydantic import BaseModel


class UkrPoshtaModel(BaseModel):
    street: str
    house_number: str
    apartment_number: Optional[str] = ""
    city: str
    region: Optional[str] = ""
    country: Optional[str] = ""
    post_code: str


class UkrPoshtaCreate(UkrPoshtaModel):
    pass


class UkrPoshtaPartialUpdate(BaseModel):
    street: str | None = None
    house_number: str | None = None
    apartment_number: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    post_code: str | None = None


class UkrPoshtaResponse(UkrPoshtaModel):
    id: int

    class Config:
        orm_mode = True

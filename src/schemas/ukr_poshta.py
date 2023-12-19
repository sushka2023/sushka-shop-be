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


class UkrPoshtaResponse(UkrPoshtaModel):
    id: int

    class Config:
        orm_mode = True

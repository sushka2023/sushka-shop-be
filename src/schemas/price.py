from typing import Optional, List

from pydantic import BaseModel, Field, validator


class PriceModel(BaseModel):
    product_id: int
    weight: str = Field(min_length=1, max_length=20)
    price: float
    old_price: Optional[float]
    quantity: int
    is_active: bool
    promotional: bool

    @validator('price', 'old_price', pre=True)
    def format_float(cls, price):
        return '{:.2f}'.format(price)


class PriceResponse(BaseModel):
    id: int
    product_id: Optional[int]
    weight: str
    price: float
    old_price: Optional[float]
    quantity: int
    is_active: bool
    is_deleted: bool
    promotional: bool

    class Config:
        orm_mode = True


class PriceArchiveModel(BaseModel):
    id: int


class TotalPriceModel(BaseModel):
    id: List[int]


class TotalPriceResponse(BaseModel):
    total_price: str

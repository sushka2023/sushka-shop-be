from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.database.models import Product


class PriceModel(BaseModel):
    product_id: int
    weight: str = Field(min_length=1, max_length=20)
    price: float
    old_price: Optional[float]
    quantity: int

    @validator('price', 'old_price', pre=True)
    def format_float(cls, price):
        return '{:.2f}'.format(price)


class PriceResponse(BaseModel):
    id: int
    product_id: int
    weight: str
    price: float
    old_price: Optional[float]
    quantity: int
    is_deleted: bool

    class Config:
        orm_mode = True


class PriceArchiveModel(BaseModel):
    id: int

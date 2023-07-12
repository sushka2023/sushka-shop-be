from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import Product


class PriceModel(BaseModel):
    product_id: int
    weight: str = Field(min_length=1, max_length=20)
    price: float
    old_price: Optional[float]
    quantity: int


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

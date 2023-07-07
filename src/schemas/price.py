from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import Product


class PriceModel(BaseModel):
    product: Product
    weight: str = Field(min_length=1, max_length=20)
    price: float
    old_price: Optional[float]


class PriceResponse(BaseModel):
    id: int
    product_id: int
    weight: str
    price: float
    old_price: Optional[float]

    class Config:
        orm_mode = True
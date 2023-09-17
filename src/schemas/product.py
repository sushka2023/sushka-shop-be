from datetime import datetime
from typing import Optional, List, Tuple

from pydantic import BaseModel, Field

from src.database.models import ProductCategory, Price, Image
from src.schemas.images import ImageResponse
from src.schemas.price import PriceResponse


class ProductModel(BaseModel):
    name: str = Field(min_length=6, max_length=150)
    description: str = Field(min_length=20, max_length=400)
    product_category_id: int
    promotional: bool
    new_product: bool
    is_popular: bool
    images: List[ImageResponse]


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    product_category_id: int
    promotional: bool
    new_product: bool
    is_popular: bool
    images: List[ImageResponse]

    class Config:
        orm_mode = True


class ProductWithPricesResponse(BaseModel):
    product: ProductResponse
    prices: List[PriceResponse]


class ProductArchiveModel(BaseModel):
    id: int

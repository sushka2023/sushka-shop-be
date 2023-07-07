from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import ProductCategory, Price, Image


class ProductModel(BaseModel):
    name: str = Field(min_length=6, max_length=150)
    description: str = Field(min_length=20, max_length=400)
    product_category: ProductCategory
    promotional: bool
    new_product: bool


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    product_category: ProductCategory
    prices: [Price]
    images: [Image]
    promotional: bool
    new_product: bool

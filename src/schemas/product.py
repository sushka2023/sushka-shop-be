from datetime import datetime
from typing import Optional, List, Tuple, Type

from pydantic import BaseModel, Field

from src.database.models import ProductCategory, Price, Image, ProductSubCategory
from src.schemas.images import ImageResponse
from src.schemas.price import PriceResponse
from src.schemas.product_sub_category import ProductSubCategoryResponse


class ProductModel(BaseModel):
    name: str = Field(min_length=6, max_length=150)
    description: str = Field(min_length=20, max_length=400)
    product_category_id: int
    promotional: bool
    new_product: bool
    is_popular: bool


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    product_category_id: int
    promotional: bool
    new_product: bool
    is_popular: bool
    is_favorite: bool
    sub_categories: List[ProductSubCategoryResponse]

    class Config:
        orm_mode = True


class ProductWithPricesAndImagesResponse(BaseModel):
    product: ProductResponse
    prices: List[PriceResponse]
    images: List[ImageResponse]


class ProductArchiveModel(BaseModel):
    id: int

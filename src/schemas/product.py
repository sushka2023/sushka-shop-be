from typing import List

from pydantic import BaseModel, Field

from src.database.models import ProductStatus
from src.schemas.images import ImageResponse
from src.schemas.price import PriceResponse
from src.schemas.product_sub_category import ProductSubCategoryResponse


class ProductModel(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=150)
    product_category_id: int
    sub_categories_id: List[int]
    new_product: bool
    is_popular: bool
    product_status: ProductStatus


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    product_category_id: int
    new_product: bool
    is_popular: bool
    is_favorite: bool
    product_status: ProductStatus
    sub_categories: List[ProductSubCategoryResponse] = []
    images: List[ImageResponse]
    prices: List[PriceResponse]

    class Config:
        orm_mode = True


class ProductArchiveModel(BaseModel):
    id: int


class ProductWithTotalResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int


class ProductResponseForOrder(BaseModel):
    id: int
    name: str
    description: str
    product_category_id: int
    new_product: bool
    is_popular: bool
    is_favorite: bool
    product_status: ProductStatus
    images: List[ImageResponse]

    class Config:
        orm_mode = True

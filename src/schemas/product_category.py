from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import Product


class ProductCategoryModel(BaseModel):
    name: str = Field(min_length=3, max_length=100)


class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    is_deleted: bool

    class Config:
        orm_mode = True


class ProductCategoryArchiveModel(BaseModel):
    id: int


class ProductCategoryIdModel(BaseModel):
    id: int


class ProductCategoryEditModel(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=100)

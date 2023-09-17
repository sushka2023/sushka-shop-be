from typing import Optional, List

from pydantic import BaseModel, Field

from src.database.models import ImageType


class ImageModel(BaseModel):
    description: str = Field(min_length=10, max_length=255)
    image_type: ImageType


class ImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    description: str = Field(min_length=10, max_length=255)
    image_type: ImageType

    class Config:
        orm_mode = True

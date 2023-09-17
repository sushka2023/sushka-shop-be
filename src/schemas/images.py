from typing import Optional, List

from pydantic import BaseModel, Field


class ImageModel(BaseModel):
    product_id: int
    image_url: str
    description: str = Field(min_length=10, max_length=255)


class ImageResponse(BaseModel):
    id: int
    product_id: int
    image_url: str
    description: str = Field(min_length=10, max_length=255)

    class Config:
        orm_mode = True

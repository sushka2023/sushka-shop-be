from pydantic import BaseModel

from src.schemas.product import ProductResponse


class BasketItemsModel(BaseModel):
    product_id: int
    quantity: int = 1


class BasketItemsResponse(BaseModel):
    id: int
    basket_id: int
    product: ProductResponse
    quantity: int

    class Config:
        orm_mode = True

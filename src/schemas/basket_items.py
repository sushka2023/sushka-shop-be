from typing import Optional

from pydantic import BaseModel

from src.schemas.product import ProductResponse


class BasketItemsModel(BaseModel):
    product_id: int
    quantity: int = 1
    price_id_by_the_user: Optional[int]


class BasketItemsRemoveModel(BaseModel):
    product_id: int
    price_id_by_the_user: Optional[int]


class BasketItemsResponse(BaseModel):
    id: int
    basket_id: int
    product: ProductResponse
    quantity: int
    price_id_by_the_user: int

    class Config:
        orm_mode = True


class ChangeQuantityBasketItemsModel(BaseModel):
    id: int
    quantity: int


class ChangePriceBasketItemsModel(BaseModel):
    id: int
    price_id: int


class BasketItemsMessageResponse(BaseModel):
    message: str

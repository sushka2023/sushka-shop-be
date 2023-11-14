from pydantic import BaseModel


class BasketItemsModel(BaseModel):
    product_id: int
    quantity: int = 1


class BasketItemsResponse(BaseModel):
    id: int
    basket_id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

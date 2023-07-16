from pydantic import BaseModel


class BasketModel(BaseModel):
    user_id: int


class BasketResponse(BaseModel):
    id: int
    user_id: int

    class Config:
        orm_mode = True

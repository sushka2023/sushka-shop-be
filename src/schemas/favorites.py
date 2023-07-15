from pydantic import BaseModel


class ProductCategoryModel(BaseModel):
    user_id: int


class ProductCategoryResponse(BaseModel):
    id: int
    user_id: str

    class Config:
        orm_mode = True

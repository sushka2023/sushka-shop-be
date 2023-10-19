from pydantic import BaseModel, Field


class ProductSubCategoryModel(BaseModel):
    name: str = Field(min_length=3, max_length=100)


class ProductSubCategoryResponse(BaseModel):
    id: int
    name: str
    is_deleted: bool

    class Config:
        orm_mode = True


class ProductSubCategoryArchiveModel(BaseModel):
    id: int


class ProductSubCategoryIdModel(BaseModel):
    id: int


class ProductSubCategoryEditModel(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=100)

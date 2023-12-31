from pydantic import BaseModel


class FavoriteModel(BaseModel):
    user_id: int


class FavoriteResponse(BaseModel):
    id: int
    user_id: int

    class Config:
        orm_mode = True

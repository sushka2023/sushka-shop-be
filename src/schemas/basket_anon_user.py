from pydantic import BaseModel


class AnonymousUserResponse(BaseModel):
    id: int
    user_anon_id: str

    class Config:
        orm_mode = True


class BasketNumberAnonUserResponse(BaseModel):
    id: int
    anonymous_user_id: int
    anonymous_user: AnonymousUserResponse

    class Config:
        orm_mode = True

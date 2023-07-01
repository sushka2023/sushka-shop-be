from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserModel(BaseModel):
    email: str = Field(min_length=6, max_length=120)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    password_checksum: str = Field(min_length=8, max_length=50)


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_blocked: bool
    is_deleted: bool
    password_checksum: str
    refresh_token: Optional[str]

    class Config:
        orm_mode = True

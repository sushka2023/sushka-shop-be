from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import Role


class UserModel(BaseModel):
    email: str = Field(min_length=6, max_length=150)
    first_name: str = Field(min_length=3, max_length=150)
    last_name: str = Field(min_length=3, max_length=150)
    password_checksum: str = Field(min_length=8, max_length=255)


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    created_at: datetime
    updated_at: Optional[datetime]
    is_blocked: bool
    is_deleted: bool
    is_active: bool
    refresh_token: Optional[str]

    class Config:
        orm_mode = True


class UserChangeRole(BaseModel):
    id: int
    role: Role
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordModel(BaseModel):
    password_checksum: str = Field(min_length=8, max_length=255)

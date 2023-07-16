from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import baskets as repository_baskets
from src.schemas.baskets import BasketResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/baskets", tags=["basket"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post("/create",
             response_model=BasketResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create(current_user: User = Depends(auth_service.get_current_user),
                 db: Session = Depends(get_db)):
    basket = await repository_baskets.baskets(current_user, db)
    if basket:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    new_basket = await repository_baskets.create(current_user, db)
    return new_basket

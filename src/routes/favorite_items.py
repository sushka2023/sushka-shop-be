from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import favorite_items as repository_favorite_items
from src.repository import favorites as repository_favorites
from src.schemas.favorite_items import FavoriteItemsResponse, FavoriteItemsModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/favorite_items", tags=["favorite_items"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post("/add",
             response_model=FavoriteItemsResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def add_to_favorites(body: FavoriteItemsModel,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    favorite = await repository_favorites.favorites(current_user, db)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    add_product_to_favorites = await repository_favorite_items.create(body, favorite, db)
    return add_product_to_favorites


@router.get("/", response_model=List[FavoriteItemsResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def favorite_items(current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    favorite_items_ = await repository_favorite_items.favorite_items(current_user, db)
    if favorite_items_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return favorite_items_


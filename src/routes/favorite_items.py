from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import favorite_items as repository_favorite_items
from src.repository import favorites as repository_favorites
from src.repository import products as repository_products
from src.schemas.favorite_items import FavoriteItemsResponse, FavoriteItemsModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/favorite_items", tags=["favorite_items"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/", response_model=List[FavoriteItemsResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def favorite_items(current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    favorite_items_ = await repository_favorite_items.favorite_items(current_user, db)
    if favorite_items_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return favorite_items_


@router.post("/add",
             response_model=FavoriteItemsResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def add_to_favorites(body: FavoriteItemsModel,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    favorite = await repository_favorites.favorites(current_user, db)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product = await repository_products.product_by_id(body.product_id, db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    favorite_item = await repository_favorite_items.favorite_item(body, current_user, db)
    if favorite_item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    add_product_to_favorites = await repository_favorite_items.create(body, favorite, db)
    return add_product_to_favorites


@router.delete("/remove",
               dependencies=[Depends(allowed_operation_admin_moderator_user)],
               status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(body: FavoriteItemsModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    favorite = await repository_favorites.favorites(current_user, db)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    favorite_item = await repository_favorite_items.favorite_item(body, current_user, db)
    if not favorite_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    product_from_fav = await repository_favorite_items.get_f_item_from_product_id(body.product_id, db)  # get product from favorite
    await repository_favorite_items.remove(product_from_fav, db)  # Remove product from favorite
    return None

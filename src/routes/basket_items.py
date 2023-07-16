from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import basket_items as repository_basket_items
from src.repository import baskets as repository_baskets
from src.repository import products as repository_products
from src.schemas.basket_items import BasketItemsModel, BasketItemsResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/basket_items", tags=["basket_items"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/", response_model=List[BasketItemsResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def basket_items(current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    basket_items_ = await repository_basket_items.basket_items(current_user, db)
    if basket_items_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return basket_items_


@router.post("/add",
             response_model=BasketItemsResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def add_to_favorites(body: BasketItemsModel,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    basket = await repository_baskets.baskets(current_user, db)
    if not basket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product = await repository_products.product_by_id(body.product_id, db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_item = await repository_basket_items.basket_item(body, current_user, db)
    if basket_item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    add_product_to_basket = await repository_basket_items.create(body, basket, db)
    return add_product_to_basket


@router.delete("/remove",
               dependencies=[Depends(allowed_operation_admin_moderator_user)],
               status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(body: BasketItemsModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    basket = await repository_baskets.baskets(current_user, db)
    if not basket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_item = await repository_basket_items.basket_item(body, current_user, db)
    if not basket_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    product_from_basket = await repository_basket_items.get_b_item_from_product_id(body.product_id, db)  # get product from favorite
    await repository_basket_items.remove(product_from_basket, db)  # Remove product from favorite
    return None

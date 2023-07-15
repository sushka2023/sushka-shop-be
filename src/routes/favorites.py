from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import prices as repository_prices
from src.repository import products as repository_products
from src.schemas.price import PriceResponse, PriceModel, PriceArchiveModel
from src.services.roles import RoleAccess

router = APIRouter(prefix="/favorites", tags=["favorite"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.post("/create",
             response_model=ProductCategoryResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_category(body: ProductCategoryModel,
                          db: Session = Depends(get_db)):
    product_category = await repository_product_categories.product_category_by_name(body.name, db)
    if product_category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists.")
    new_product_category = await repository_product_categories.create_product_category(body, db)
    return new_product_category
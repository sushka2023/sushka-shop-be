from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role, BlacklistToken
from src.repository import users as repository_users
from src.repository import product_categories as repository_product_categories
from src.services.auth import auth_service
from src.schemas.product_category import ProductCategoryModel, ProductCategoryResponse
from src.services.roles import RoleAccess

router = APIRouter(prefix="/product_category", tags=["product_category"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.post("/create_category", response_model=ProductCategoryResponse, dependencies=[Depends(allowed_operation_admin_moderator)])
async def create_category(body: ProductCategoryModel,
                          db: Session = Depends(get_db)):
    product_category = await repository_product_categories.product_category_by_name(body.name, db)
    if product_category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists.")
    new_product_category = await repository_product_categories.create_product_category(body, db)
    return new_product_category

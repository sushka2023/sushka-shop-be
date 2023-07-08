from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import product_categories as repository_product_categories
from src.schemas.product_category import ProductCategoryModel, ProductCategoryResponse, ProductCategoryArchiveModel
from src.services.roles import RoleAccess

router = APIRouter(prefix="/product_category", tags=["product_category"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/product_categories", response_model=List[ProductCategoryResponse])
async def product_categories(db: Session = Depends(get_db)):
    prod_categories = await repository_product_categories.product_categories(db)
    if prod_categories is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return prod_categories


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


@router.put("/archive_product_category",
            response_model=ProductCategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product_category(body: ProductCategoryArchiveModel, db: Session = Depends(get_db)):
    product_category = await repository_product_categories.product_category_by_id(body.id, db)
    if product_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    if product_category.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product category already archive.")
    archive_prod_cat = await repository_product_categories.archive_product_category(body.id, db)
    return archive_prod_cat


@router.put("/return_archive_product_category",
            response_model=ProductCategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductCategoryArchiveModel, db: Session = Depends(get_db)):
    product_category = await repository_product_categories.product_category_by_id(body.id, db)
    if product_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    if product_category.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The product category is not archived.")
    return_archive_prod_cat = await repository_product_categories.return_archive_product_category(body.id, db)
    return return_archive_prod_cat

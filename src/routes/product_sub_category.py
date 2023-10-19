from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import product_sub_categories as repository_product_sub_categories
from src.schemas.product_sub_category import ProductSubCategoryModel, ProductSubCategoryResponse, ProductSubCategoryArchiveModel, \
    ProductSubCategoryEditModel
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/product_sub_category", tags=["product_sub_category"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/all_for_crm", response_model=List[ProductSubCategoryResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def product_sub_categories_for_crm(db: Session = Depends(get_db)):

    prod_sub_categories = await repository_product_sub_categories.product_sub_categories_all_for_crm(db)
    if prod_sub_categories is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return prod_sub_categories


@router.post("/create",
             response_model=ProductSubCategoryResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_sub_category(body: ProductSubCategoryModel,
                              db: Session = Depends(get_db)):

    product_sub_category = await repository_product_sub_categories.product_sub_category_by_name(body.name, db)
    if product_sub_category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    new_sub_product_category = await repository_product_sub_categories.create_sub_product_category(body, db)

    await delete_cache_in_redis()

    return new_sub_product_category


@router.patch("/edit",
              response_model=ProductSubCategoryResponse,
              dependencies=[Depends(allowed_operation_admin_moderator)])
async def edit_sub_category(body: ProductSubCategoryEditModel,
                            db: Session = Depends(get_db)):

    product_sub_category = await repository_product_sub_categories.product_sub_category_by_id(body.id, db)
    if not product_sub_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    edit_product_sub_category = await repository_product_sub_categories.edit_sub_product_category(body, product_sub_category, db)

    await delete_cache_in_redis()

    return edit_product_sub_category


@router.put("/archive",
            response_model=ProductSubCategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product_sub_category(body: ProductSubCategoryArchiveModel, db: Session = Depends(get_db)):

    product_sub_category = await repository_product_sub_categories.product_sub_category_by_id(body.id, db)
    if product_sub_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product_sub_category.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    archive_prod_sub_cat = await repository_product_sub_categories.archive_sub_product_category(body.id, db)

    await delete_cache_in_redis()

    return archive_prod_sub_cat


@router.put("/unarchive",
            response_model=ProductSubCategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def unarchive_product_sub_category(body: ProductSubCategoryArchiveModel, db: Session = Depends(get_db)):

    product_sub_category = await repository_product_sub_categories.product_sub_category_by_id(body.id, db)
    if product_sub_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product_sub_category.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_unarchive_prod_sub_cat = await repository_product_sub_categories.unarchive_sub_product_category(body.id, db)

    await delete_cache_in_redis()

    return return_unarchive_prod_sub_cat

from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import products as repository_products
from src.repository import product_categories as repository_product_categories
from src.schemas.product import ProductModel, ProductResponse, ProductArchiveModel
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/product", tags=["product"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/all", response_model=List[ProductResponse])
async def products(limit: int, offset: int, pr_category_id: int = None, sort: str = "name", db: Session = Depends(get_db)):
    products_ = None

    if sort not in ["id", "name", "low_price", "high_price", "low_date", "high_date"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if pr_category_id is None:
        if sort in "id":
            products_ = await repository_products.get_products_id(limit, offset, db)
        elif sort in "name":
            products_ = await repository_products.get_products_name(limit, offset, db)
        elif sort in "low_price":
            products_ = await repository_products.get_products_low_price(limit, offset, db)
        elif sort in "high_price":
            products_ = await repository_products.get_products_high_price(limit, offset, db)
        elif sort in "low_date":
            products_ = await repository_products.get_products_low_date(limit, offset, db)
        elif sort in "high_date":
            products_ = await repository_products.get_products_high_date(limit, offset, db)

    if pr_category_id:
        product_category = await repository_product_categories.product_category_by_id(pr_category_id, db)
        if product_category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

        if sort in "id":
            products_ = await repository_products.get_products_id_by_category_id(limit, offset, pr_category_id, db)
        elif sort in "name":
            products_ = await repository_products.get_products_name_by_category_id(limit, offset, pr_category_id, db)
        elif sort in "low_price":
            products_ = await repository_products.get_products_low_price_by_category_id(limit, offset, pr_category_id, db)
        elif sort in "high_price":
            products_ = await repository_products.get_products_high_price_by_category_id(limit, offset, pr_category_id, db)
        elif sort in "low_date":
            products_ = await repository_products.get_products_low_date_by_category_id(limit, offset, pr_category_id, db)
        elif sort in "high_date":
            products_ = await repository_products.get_products_high_date_by_category_id(limit, offset, pr_category_id, db)

    if products_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return products_


@router.post("/create",
             response_model=ProductResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_name(body.name, db)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    new_product = await repository_products.create_product(body, db)
    return new_product


@router.put("/archive",
            response_model=ProductResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductArchiveModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_id(body.id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    archive_prod = await repository_products.archive_product(body.id, db)
    return archive_prod


@router.put("/unarchive",
            response_model=ProductResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductArchiveModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_id(body.id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_archive_prod = await repository_products.unarchive_product(body.id, db)
    return return_archive_prod

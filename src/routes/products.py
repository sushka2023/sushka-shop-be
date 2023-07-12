from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import products as repository_products
from src.schemas.product import ProductModel, ProductResponse, ProductArchiveModel
from src.services.roles import RoleAccess

router = APIRouter(prefix="/product", tags=["product"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/all", response_model=List[ProductResponse])
async def products(limit: int, offset: int, sort: str, db: Session = Depends(get_db)):
    products_ = await repository_products.get_products(limit, offset, sort, db)
    if products_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return products_


@router.post("/create",
             response_model=ProductResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_name(body.name, db)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists.")
    new_product = await repository_products.create_product(body, db)
    return new_product


@router.put("/archive_product",
            response_model=ProductResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductArchiveModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_id(body.id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    if product.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already archive.")
    archive_prod = await repository_products.archive_product(body.id, db)
    return archive_prod


@router.put("/unarchive_product",
            response_model=ProductResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductArchiveModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_id(body.id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    if product.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The product is not archived.")
    return_archive_prod = await repository_products.return_archive_product(body.id, db)
    return return_archive_prod

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import products as repository_products
from src.schemas.product import ProductModel, ProductResponse
from src.services.roles import RoleAccess

router = APIRouter(prefix="/product", tags=["product"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.post("/create_product",
             response_model=ProductResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_name(body.name, db)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists.")
    new_product = await repository_products.create_product(body, db)
    return new_product

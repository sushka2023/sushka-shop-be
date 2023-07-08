from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import prices as repository_prices
from src.repository import products as repository_products
from src.schemas.price import PriceResponse, PriceModel
from src.services.roles import RoleAccess

router = APIRouter(prefix="/price", tags=["price"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.post("/create",
             response_model=PriceResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_price(body: PriceModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_id(body.product_id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    new_price = await repository_prices.create_price(body, db)
    return new_price


@router.get("/product_prices", response_model=List[PriceResponse])
async def product_prices(id_product: int, db: Session = Depends(get_db)):
    prod_prices = await repository_prices.price_by_product_id(id_product, db)
    if prod_prices is None or len(prod_prices) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return prod_prices

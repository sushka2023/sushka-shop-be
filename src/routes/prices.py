from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import prices as repository_prices
from src.repository import products as repository_products
from src.schemas.price import PriceResponse, PriceModel, PriceArchiveModel, TotalPriceResponse, TotalPriceModel
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/price", tags=["price"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/product", response_model=List[PriceResponse])
async def product_prices(id_product: int, db: Session = Depends(get_db)):
    prod_prices = await repository_prices.price_by_product_id(id_product, db)
    if prod_prices is None or len(prod_prices) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return prod_prices


@router.post("/create",
             response_model=PriceResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_price(body: PriceModel, db: Session = Depends(get_db)):
    product = await repository_products.product_by_id(body.product_id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    new_price = await repository_prices.create_price(body, db)
    return new_price


@router.put("/archive",
            response_model=PriceResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: PriceArchiveModel, db: Session = Depends(get_db)):
    price = await repository_prices.price_by_id(body.id, db)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if price.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    archive_price = await repository_prices.archive_price(body.id, db)
    return archive_price


@router.put("/unarchive",
            response_model=PriceResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: PriceArchiveModel, db: Session = Depends(get_db)):
    price = await repository_prices.price_by_id(body.id, db)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if price.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_archive_price = await repository_prices.unarchive_price(body.id, db)
    return return_archive_price


@router.post("/total_price", response_model=TotalPriceResponse)
async def total_price(body: TotalPriceModel, db: Session = Depends(get_db)):
    total = await repository_prices.calculate_total_price(body.id, db)

    if total is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    total = TotalPriceResponse(total_price=total)
    return total

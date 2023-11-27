from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import prices as repository_prices
from src.repository import products as repository_products
from src.schemas.price import PriceResponse, PriceModel, PriceArchiveModel, TotalPriceResponse, TotalPriceModel
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/price", tags=["price"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/product", response_model=List[PriceResponse])
async def product_prices(id_product: int, db: Session = Depends(get_db)):
    """
    The product_prices function returns a list of prices for the product with the given id.
        If no such product exists, it raises an HTTP 404 error.

    Args:
        id_product: int: Get the product id from the url
        db: Session: Get the database session

    Returns:
        A list of prices for a given product
    """
    prod_prices = await repository_prices.price_by_product_id(id_product, db)
    if prod_prices is None or len(prod_prices) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return prod_prices


@router.post("/create",
             response_model=PriceResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_price(body: PriceModel, db: Session = Depends(get_db)):
    """
    The create_price function creates a new price in the database.
        The function takes a PriceModel object as input and returns the newly created price.

    Args:
        body: PriceModel: Get the data from the request body
        db: Session: Pass the database session to the repository

    Returns:
        A new price object
    """
    product = await repository_products.product_by_id(body.product_id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    new_price = await repository_prices.create_price(body, db)

    await delete_cache_in_redis()

    return new_price


@router.put("/archive",
            response_model=PriceResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: PriceArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_product function is used to archive a product.
        It takes in the id of the product and archives it.
        If the product does not exist, it returns a 404 error code with an appropriate message.
        If the product has already been archived, it returns a 409 error code with an appropriate message.

    Args:
        body: PriceArchiveModel: Get the id of the price to be archived
        db: Session: Get the database session

    Returns:
        A pricearchivemodel object
    """
    price = await repository_prices.price_by_id(body.id, db)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if price.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    archive_price = await repository_prices.archive_price(body.id, db)

    await delete_cache_in_redis()

    return archive_price


@router.put("/unarchive",
            response_model=PriceResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: PriceArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_product function takes a PriceArchiveModel object as input, and returns the archived price.
    The function first checks if the price exists in the database. If it does not exist, an HTTP 404 error is raised.
    If it does exist but has already been deleted (is_deleted = True), an HTTP 409 error is raised to indicate that there
    is a conflict between what was requested and what currently exists in the database.

    Args:
        body: PriceArchiveModel: Get the id of the price to be archived
        db: Session: Pass the database session to the function

    Returns:
        A price model
    """
    price = await repository_prices.price_by_id(body.id, db)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if price.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_archive_price = await repository_prices.unarchive_price(body.id, db)

    await delete_cache_in_redis()

    return return_archive_price


@router.post("/total_price", response_model=TotalPriceResponse)
async def total_price(body: TotalPriceModel, db: Session = Depends(get_db)):
    """
    The total_price function calculates the total price of a given order.
        The function takes in an id and returns the total price of that order.

    Args:
        body: TotalPriceModel: Get the id of the product from the request body
        db: Session: Get the database session

    Returns:
        The total price of the order, which is calculated by adding up all the prices of
    """
    total = await repository_prices.calculate_total_price(body.id, db)

    if total is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    total = TotalPriceResponse(total_price=total)
    return total

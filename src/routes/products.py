import pickle
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.caching import get_redis
from src.database.models import Role
from src.repository import products as repository_products
from src.repository.products import product_by_id
from src.schemas.product import ProductModel, ProductResponse, ProductArchiveModel, ProductWithPricesAndImagesResponse
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex
from src.services.products import get_products_by_sort, get_products_by_sort_and_category_id

router = APIRouter(prefix="/product", tags=["product"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/all", response_model=List[ProductWithPricesAndImagesResponse])
async def products(limit: int, offset: int, pr_category_id: int = None, sort: str = "name", db: Session = Depends(get_db)):
    """
    The products function returns a list of products.

    Args:
        limit: int: Limit the number of products returned
        offset: int: Specify the offset of the first product to be returned
        pr_category_id: int: Filter products by category
        sort: str: Sort the products by "id", "name", "low_price", "high_price", "low_date", "high_date"
        db: Session: Pass the database connection to the function

    Returns:
        A list of products
    """
    # Redis client
    redis_client = get_redis()
    # List of allowed sorts
    allowed_sorts = ["id", "name", "low_price", "high_price", "low_date", "high_date"]
    if sort not in allowed_sorts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid sort parameter. Allowed values: {', '.join(allowed_sorts)}")

    # We collect the key for caching
    key = f"products_{sort}_limit:{limit}:offset:{offset}:pr_category_id:{pr_category_id}"

    cached_products = None

    if redis_client:
        # We check whether the data is present in the Redis cache
        cached_products = redis_client.get(key)

    if not cached_products:
        # The data is not found in the cache, we get it from the database
        if pr_category_id is None:
            products_ = await get_products_by_sort(sort, limit, offset, db)
        else:
            products_ = await get_products_by_sort_and_category_id(sort, limit, offset, pr_category_id, db)

        # We store the data in the Redis cache and set the lifetime to 1800 seconds
        if redis_client:
            redis_client.set(key, pickle.dumps(products_))
            redis_client.expire(key, 1800)

    else:
        # The data is found in the Redis cache, we extract it from there
        products_ = pickle.loads(cached_products)

    if not products_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return products_


@router.post("/create",
             response_model=ProductResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductModel, db: Session = Depends(get_db)):
    """
    The create_product function creates a new product in the database.

    Args:
        body: ProductModel: Validate the request body
        db: Session: Pass the database session to the repository layer

    Returns:
        A productmodel object
    """
    product = await repository_products.product_by_name(body.name, db)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    new_product = await repository_products.create_product(body, db)
    return new_product


@router.put("/archive",
            response_model=ProductResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_product function is used to archive a product.
        The function takes in the id of the product to be archived and returns an object containing information about that product.
        If no such id exists, it raises a 404 error.


    Args:
        body: ProductArchiveModel: Get the id of the product to be archived
        db: Session: Get the database session

    Returns:
        A product object
    """
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
async def unarchive_product(body: ProductArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_product function is used to unarchive a product.
        The function takes in the id of the product and returns an object containing information about that product.

    Args:
        body: ProductArchiveModel: Get the id of the product to be archived
        db: Session: Get the database session

    Returns:
        A product object
    """
    product = await repository_products.product_by_id(body.id, db)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_archive_prod = await repository_products.unarchive_product(body.id, db)
    return return_archive_prod


@router.get("/{product_id}", response_model=ProductWithPricesAndImagesResponse)
async def get_one_product(product_id: int, db: Session = Depends(get_db)):
    # Redis client
    redis_client = get_redis()

    # We collect the key for caching
    key = f"products_:{product_id}"

    cached_products = None

    if redis_client:
        # We check whether the data is present in the Redis cache
        cached_products = redis_client.get(key)

    if not cached_products:
        # The data is not found in the cache, we get it from the database
        product = await product_by_id(product_id, db)

        # We store the data in the Redis cache and set the lifetime to 1800 seconds
        if redis_client:
            redis_client.set(key, pickle.dumps(product))
            redis_client.expire(key, 1800)

    else:
        # The data is found in the Redis cache, we extract it from there
        product = pickle.loads(cached_products)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return product

import pickle
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role
from src.repository import product_categories as repository_product_categories
from src.schemas.product_category import ProductCategoryModel, ProductCategoryResponse, ProductCategoryArchiveModel
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/product_category", tags=["product_category"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/all", response_model=List[ProductCategoryResponse])
async def product_categories(db: Session = Depends(get_db)):
    """
    The product_categories function returns a list of all product categories in the database.

    Args:
        db: Session: Access the database

    Returns:
        A list of product categories
    """
    # Redis client
    redis_client = get_redis()

    # We collect the key for caching
    key = f"product_categories"

    cached_products = None

    if redis_client:
        # We check whether the data is present in the Redis cache
        cached_products = redis_client.get(key)

    if not cached_products:
        # The data is not found in the cache, we get it from the database
        prod_categories = await repository_product_categories.product_categories(db)

        if prod_categories is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

            # We store the data in the Redis cache and set the lifetime to 1800 seconds
        if redis_client:
            redis_client.set(key, pickle.dumps(prod_categories))
            redis_client.expire(key, 1800)

    else:
        # The data is found in the Redis cache, we extract it from there
        prod_categories = pickle.loads(cached_products)

    return prod_categories


@router.get("/all_for_crm", response_model=List[ProductCategoryResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def product_categories_for_crm(db: Session = Depends(get_db)):
    """
    The product_categories function returns a list of all product categories in the database.

    Args:
        db: Session: Access the database

    Returns:
        A list of product categories
    """
    prod_categories = await repository_product_categories.product_categories_all_for_crm(db)
    if prod_categories is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return prod_categories


@router.post("/create",
             response_model=ProductCategoryResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_category(body: ProductCategoryModel,
                          db: Session = Depends(get_db)):
    """
    The create_category function creates a new product category.
        Args:
            body (ProductCategoryModel): The ProductCategoryModel object to be created.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    Args:
        body: ProductCategoryModel: Get the name of the product category to be created
        db: Session: Get the database session

    Returns:
        A productcategorymodel object
    """
    product_category = await repository_product_categories.product_category_by_name(body.name, db)
    if product_category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    new_product_category = await repository_product_categories.create_product_category(body, db)

    await delete_cache_in_redis()

    return new_product_category


@router.put("/archive",
            response_model=ProductCategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product_category(body: ProductCategoryArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_product_category function is used to archive a product category.
        The function takes in the id of the product category to be archived and returns an object containing information about
        the archived product category.

    Args:
        body: ProductCategoryArchiveModel: Get the id of the product category to be archived
        db: Session: Access the database

    Returns:
        A productcategoryarchivemodel object
    """
    product_category = await repository_product_categories.product_category_by_id(body.id, db)
    if product_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product_category.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    archive_prod_cat = await repository_product_categories.archive_product_category(body.id, db)

    await delete_cache_in_redis()

    return archive_prod_cat


@router.put("/unarchive",
            response_model=ProductCategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_product(body: ProductCategoryArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_product function is used to unarchive a product category.
        The function takes in the id of the product category and returns an object containing information about that
        product category.

    Args:
        body: ProductCategoryArchiveModel: Get the id of the product category to be deleted
        db: Session: Get the database session

    Returns:
        A productcategory object
    """
    product_category = await repository_product_categories.product_category_by_id(body.id, db)
    if product_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if product_category.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_archive_prod_cat = await repository_product_categories.unarchive_product_category(body.id, db)

    await delete_cache_in_redis()

    return return_archive_prod_cat

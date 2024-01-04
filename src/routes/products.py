import pickle
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.caching import get_redis
from src.database.models import Role, ProductStatus
from src.repository import products as repository_products
from src.repository.prices import price_by_product
from src.repository.product_sub_categories import insert_sub_category_for_product
from src.repository.products import product_by_id, get_products_all_for_crm
from src.schemas.images import ImageResponse
from src.schemas.product import ProductModel, ProductResponse, ProductArchiveModel
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.cloud_image import CloudImage
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex
from src.services.products import get_products_by_sort, get_products_by_sort_and_category_id

router = APIRouter(prefix="/product", tags=["product"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/all", response_model=List[ProductResponse])
async def products(limit: int, offset: int, weight: str = None, pr_category_id: int = None, sort: str = "low_price", db: Session = Depends(get_db)):
    """
    The products function returns a list of products.
        The function accepts the following parameters:
            limit - number of products to return (default = 10)
            offset - number of products to skip (default = 0)
            weight - product weight in grams, if specified, only those with this weight will be returned (optional)
                     If not specified, all weights are considered. Allowed values: &quot;100&quot;, &quot;200&quot;, &quot;300&quot; and so on up to 1000.
                     Any other value is invalid and will result in an error response from the server.

    :param limit: int: Limit the number of products returned
    :param offset: int: Skip the first offset records
    :param weight: str: Filter products by weight
    :param pr_category_id: int: Filter the products by category
    :param sort: str: Sort the products by id, name, low_price or high_price
    :param db: Session: Access the database
    :return: A list of products
    """
    # Redis client
    redis_client = get_redis()
    # List of allowed sorts
    allowed_sorts = ["id", "name", "low_price", "high_price", "low_date", "high_date"]
    if sort not in allowed_sorts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid sort parameter. Allowed values: {', '.join(allowed_sorts)}")

    # We collect the key for caching
    key = f"limit_{limit}:offset_{offset}:products_{sort}:pr_category_id_{pr_category_id}:weight_{weight}"

    cached_products = None

    if redis_client:
        # We check whether the data is present in the Redis cache
        cached_products = redis_client.get(key)

    if not cached_products:
        # The data is not found in the cache, we get it from the database
        products_ = list()
        if not weight:
            if not pr_category_id:
                products_ = await get_products_by_sort(limit=limit, offset=offset, sort=sort, db=db)
            elif pr_category_id:
                products_ = await get_products_by_sort_and_category_id(limit=limit, offset=offset, sort=sort, pr_category_id=pr_category_id, db=db)
        elif weight:
            if not pr_category_id:
                products_ = await get_products_by_sort(limit=limit, offset=offset, sort=sort, weight=weight, db=db)
            elif pr_category_id:
                products_ = await get_products_by_sort_and_category_id(limit=limit, offset=offset, sort=sort, pr_category_id=pr_category_id, weight=weight, db=db)

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


@router.get("/all_for_crm",
            response_model=List[ProductResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def products_for_crm(limit: int, offset: int, pr_status: ProductStatus = None, pr_category_id: int = None, db: Session = Depends(get_db)):

    """
    The products_for_crm function returns a list of products for the CRM.

    :param limit: int: Limit the number of products returned
    :param offset: int: Indicate the number of records to skip
    :param pr_status: ProductStatus: Filter products by status
    :param pr_category_id: int: Filter the products by category
    :param db: Session: Pass the database connection to the function
    :return: A list of products
    """
    # Redis client
    redis_client = get_redis()

    key = f"limit_{limit}:offset_{offset}:pr_category_id_{pr_category_id}:pr_status_{pr_status}"

    cached_products = None

    if redis_client:
        # We check whether the data is present in the Redis cache
        cached_products = redis_client.get(key)

    products_ = None

    if not cached_products:
        # The data is not found in the cache, we get it from the database
        if not pr_category_id and not pr_status:
            products_ = await repository_products.get_products_all_for_crm(limit, offset, db)
        elif pr_category_id and not pr_status:
            products_ = await repository_products.get_products_all_for_crm_pr_category_id(limit, offset, pr_category_id, db)
        elif not pr_category_id and pr_status:
            products_ = await repository_products.get_products_all_for_crm_pr_status(limit, offset, pr_status, db)
        elif pr_category_id and pr_status:
            products_ = await repository_products.get_products_all_for_crm_pr_status_and_pr_category_id(limit, offset, pr_category_id, pr_status, db)

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
            body (ProductModel): The ProductModel object to be created.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    :param body: ProductModel: Validate the request body
    :param db: Session: Get the database session
    :return: A productresponse object
    :doc-author: Trelent
    """
    product = await repository_products.product_by_name(body.name, db)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    # TODO bugfix create product when the category does not exist...
    
    body = body.dict()

    sub_categories_ids = body.pop("sub_categories_id", [])

    new_product = await repository_products.create_product(body, db)

    # add sub_categories for product
    await insert_sub_category_for_product(new_product.id, sub_categories_ids, db)
    db.refresh(new_product)
    new_product = ProductResponse(id=new_product.id,
                                  name=new_product.name,
                                  description=new_product.description,
                                  product_category_id=new_product.product_category_id,
                                  new_product=new_product.new_product,
                                  is_popular=new_product.is_popular,
                                  is_favorite=new_product.is_favorite,
                                  product_status=new_product.product_status,
                                  sub_categories=new_product.subcategories,
                                  images=[ImageResponse(id=item.id,
                                                        product_id=item.product_id,
                                                        image_url=CloudImage.get_transformation_image(item.image_url,
                                                                                                      "product"),
                                                        description=item.description,
                                                        image_type=item.image_type,
                                                        main_image=item.main_image) for item in new_product.images],
                                  prices=await price_by_product(new_product, db))

    await delete_cache_in_redis()

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

    await delete_cache_in_redis()

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

    await delete_cache_in_redis()

    return return_archive_prod


@router.get("/{product_id}", response_model=ProductResponse)
async def get_one_product(product_id: int, db: Session = Depends(get_db)):
    """
    The get_one_product function returns a single product from the database.

    :param product_id: int: Specify the product id
    :param db: Session: Pass the database session to the function
    :return: A product by id
    :doc-author: Trelent
    """
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

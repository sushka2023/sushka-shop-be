import pickle
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role, User
from src.repository import favorite_items as repository_favorite_items
from src.repository import favorites as repository_favorites
from src.repository import products as repository_products
from src.repository.products import product_by_id
from src.schemas.favorite_items import FavoriteItemsResponse, FavoriteItemsModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/favorite_items", tags=["favorite_items"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/", response_model=List[FavoriteItemsResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def favorite_items(current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):

    # Redis client
    redis_client = get_redis()

    # We collect the key for caching
    key = f"favorite_items_current_user_id:{current_user.id}"

    cached_items = None

    if redis_client:
        # We check whether the data is present in the Redis cache
        cached_items = redis_client.get(key)

    if not cached_items:
        # The data is not found in the cache, we get it from the database
        favorite_items_ = await repository_favorite_items.favorite_items(current_user, db)

        if favorite_items_ is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

        items = list()

        for i in favorite_items_:
            product = await product_by_id(i.product_id, db)
            item = FavoriteItemsResponse(id=i.id,
                                         favorite_id=i.favorite_id,
                                         product=product)
            items.append(item)

        # We store the data in the Redis cache and set the lifetime to 1800 seconds
        if redis_client:
            redis_client.set(key, pickle.dumps(items))
            redis_client.expire(key, 1800)

    else:
        # The data is found in the Redis cache, we extract it from there
        items = pickle.loads(cached_items)

    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return items


@router.post("/add",
             response_model=FavoriteItemsResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def add_to_favorites(body: FavoriteItemsModel,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    """
    The add_to_favorites function adds a product to the user's favorites list.
        The function takes in a body of type FavoriteItemsModel, which contains the product_id of the item to be added.
        It also takes in an optional current_user parameter, which is used for authentication purposes and defaults to None.
        Finally it takes in an optional db parameter that defaults to None as well.

    Args:
        body: FavoriteItemsModel: Get the product_id from the request body
        current_user: User: Get the current user
        db: Session: Get the database session

    Returns:
        A favorite item
    """
    favorite = await repository_favorites.favorites(current_user, db)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product = await repository_products.product_by_id(body.product_id, db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    favorite_item = await repository_favorite_items.favorite_item(body, current_user, db)
    if favorite_item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    add_product_to_favorites = await repository_favorite_items.create(body, favorite, db)

    with get_redis() as redis_cl:
        redis_cl.delete(f"favorite_items_current_user_id:{current_user.id}")

    return add_product_to_favorites


@router.delete("/remove",
               dependencies=[Depends(allowed_operation_admin_moderator_user)],
               status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(body: FavoriteItemsModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The remove_product function removes a product from the user's favorite list.
        The function takes in a body of type FavoriteItemsModel, which contains the id of the product to be removed.
        It also takes in an optional current_user parameter, which is used to identify who is making this request.
        This parameter defaults to None if no user is logged in and will throw an error if no user can be found.

    Args:
        body: FavoriteItemsModel: Get the product_id from the body of the request
        current_user: User: Get the current user
        db: Session: Get the database session

    Returns:
        None
    """
    favorite = await repository_favorites.favorites(current_user, db)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    favorite_item = await repository_favorite_items.favorite_item(body, current_user, db)
    if not favorite_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    product_from_fav = await repository_favorite_items.get_f_item_from_product_id(body.product_id, db)  # get product from favorite
    await repository_favorite_items.remove(product_from_fav, db)  # Remove product from favorite

    with get_redis() as redis_cl:
        redis_cl.delete(f"favorite_items_current_user_id:{current_user.id}")

    return None

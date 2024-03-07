import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role, User
from src.repository import posts as repository_posts
from src.schemas.nova_poshta import NovaPoshtaCreate, NovaPoshtaAddressDeliveryCreate

from src.schemas.posts import (
    PostResponse,
    PostUkrPostalOffice,
    PostNovaPoshtaOffice,
    PostWarehouseResponse,
    PostAddressDeliveryResponse,
    PostUkrPoshtaResponse
)
from src.schemas.ukr_poshta import UkrPoshtaCreate
from src.services.auth import auth_service
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/posts", tags=["postal offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post(
    "/create_nova_poshta_warehouse_and_associate_with_post",
    response_model=PostWarehouseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_operation_admin_moderator_user)]
)
async def create_nova_poshta_warehouse_and_associate_with_post(
    nova_post_warehouse: NovaPoshtaCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The function creates novaposhta data and adds to an exists post for the current user.

    Args:
        nova_post_warehouse: NovaPoshtaCreate: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        Message about successfully adding novaposhta data
        A novaposhta object
    """
    nova_poshta = await repository_posts.create_nova_poshta_warehouse_and_associate_with_post(
        nova_post_warehouse=nova_post_warehouse,
        user_id=current_user.id,
        post_id=current_user.posts.id,
        db=db,
    )

    return {
        "message": "NovaPoshta created and associated with Post successfully",
        "nova_poshta_data": nova_poshta
    }


@router.post(
    "/create_nova_poshta_address_delivery_and_associate_with_post",
    response_model=PostAddressDeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_operation_admin_moderator_user)]
)
async def create_nova_poshta_address_delivery_and_associate_with_post(
    nova_post_address_delivery: NovaPoshtaAddressDeliveryCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The function creates novaposhta data and adds to an exists post for the current user.

    Args:
        nova_post_address_delivery: NovaPoshtaAddressDeliveryCreate: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        Message about successfully adding novaposhta data
        A novaposhta object
    """
    nova_poshta = await repository_posts.create_nova_poshta_address_delivery_and_associate_with_post(
        nova_post_address_delivery=nova_post_address_delivery,
        user_id=current_user.id,
        post_id=current_user.posts.id,
        db=db,
    )

    return {
        "message": "NovaPoshta created and associated with Post successfully",
        "nova_poshta_data": nova_poshta
    }


@router.post(
    "/create_ukr_poshta_and_associate_with_post",
    response_model=PostUkrPoshtaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_operation_admin_moderator_user)]
)
async def create_ukr_poshta_and_associate_with_post(
    ukr_post_address: UkrPoshtaCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The function creates ukrposhta data and adds to an exists post for the current user.

    Args:
        ukr_post_address: UkrPoshtaCreate: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        Message about successfully adding novaposhta data
        An ukrposhta object
    """
    ukr_poshta = await repository_posts.create_ukr_poshta_and_associate_with_post(
        ukr_postal_office=ukr_post_address,
        user_id=current_user.id,
        post_id=current_user.posts.id,
        db=db,
    )

    return {
        "message": "UkrPoshta created and associated with Post successfully",
        "ukr_poshta_data": ukr_poshta
    }


@router.get("/my-post-offices",
            response_model=PostResponse,
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def get_my_post_offices(current_user: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):
    """
    The function returns all post offices for current user in the database.

    Args:
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        A post object
    """
    redis_client = get_redis()

    key = f"posts_{current_user}"

    cached_posts_current_user = None

    if redis_client:
        cached_posts_current_user = redis_client.get(key)

    if not cached_posts_current_user:
        posts_data_current_user = (
            await repository_posts.get_posts_by_user_id(current_user.id, db)
        )

        if posts_data_current_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND
            )

        if redis_client:
            redis_client.set(key, pickle.dumps(posts_data_current_user))
            redis_client.expire(key, 1800)
    else:
        posts_data_current_user = pickle.loads(cached_posts_current_user)

    return posts_data_current_user


@router.delete("/remove_nova_poshta_data",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def remove_nova_poshta_data(nova_poshta_data: PostNovaPoshtaOffice,
                                  current_user: User = Depends(auth_service.get_current_user),
                                  db: Session = Depends(get_db)):
    """
    The remove_nova_poshta_data function deleted an exists post with novaposhta data for the current user.

    Args:
        nova_poshta_data: PostNovaPoshtaOffice: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        None
    """

    await repository_posts.remove_nova_postal_data_from_post(
        db=db, user_id=current_user.id, post_id=current_user.posts.id, nova_poshta_in=nova_poshta_data
    )
    await delete_cache_in_redis()


@router.delete("/remove_ukr_postal_office",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def remove_ukr_postal_office(ukr_poshta_data: PostUkrPostalOffice,
                                   current_user: User = Depends(auth_service.get_current_user),
                                   db: Session = Depends(get_db)):
    """
    The remove_ukr_postal_office function deleted an exists post with address for the current user.

    Args:
        ukr_poshta_data: PostUkrPostalOffice: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        None
    """

    await repository_posts.remove_ukr_postal_office_from_post(
        db=db, user_id=current_user.id, post_id=current_user.posts.id, ukr_poshta_in=ukr_poshta_data
    )
    await delete_cache_in_redis()

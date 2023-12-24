import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import Role, User
from src.repository import posts as repository_posts

from src.schemas.posts import PostResponse, PostUkrPostalOffice, PostMessageResponse
from src.services.auth import auth_service
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/posts", tags=["postal offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


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
        posts_data_current_user = await repository_posts.get_posts_by_user_id(current_user.id, db)

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


@router.post("/add_ukr_postal_office",
             response_model=PostMessageResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def add_ukr_postal_office(ukr_poshta_data: PostUkrPostalOffice,
                                current_user: User = Depends(auth_service.get_current_user),
                                db: Session = Depends(get_db)):
    """
    The add_ukr_postal_office function updates an exists post for the current user.

    Args:
        ukr_poshta_data: PostAddUkrPostalOffice: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        Message about successfully adding an address
    """

    await repository_posts.add_ukr_postal_office_to_post(
        db=db, user_id=current_user.id, ukr_poshta_in=ukr_poshta_data
    )
    await delete_cache_in_redis()

    return {"message": "An address of ukr postal office added successfully"}


@router.delete("/remove_ukr_postal_office",
               response_model=PostMessageResponse,
               dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def remove_ukr_postal_office(ukr_poshta_data: PostUkrPostalOffice,
                                   current_user: User = Depends(auth_service.get_current_user),
                                   db: Session = Depends(get_db)):
    """
    The remove_ukr_postal_office function deleted an exists post with address for the current user.

    Args:
        ukr_poshta_data: PostAddUkrPostalOffice: Validate the request body
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        Message about successfully deleting an address from post
    """

    await repository_posts.remove_ukr_postal_office_from_post(
        db=db, user_id=current_user.id, ukr_poshta_in=ukr_poshta_data
    )
    await delete_cache_in_redis()

    return {"message": "An address of ukr postal office from post deleted successfully"}

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import posts as repository_posts

from src.schemas.posts import PostResponse, PostUkrPostalOffice, PostMessageResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/posts", tags=["postal offices"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/",
            response_model=list[PostResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_posts(db: Session = Depends(get_db)):
    """
    The function returns a list of all post offices in the database.

    Args:
        db: Session: Access the database

    Returns:
        A list of posts
    """
    return await repository_posts.get_all_posts(db)


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
    return await repository_posts.get_posts_by_user_id(current_user.id, db)


@router.post("/create",
             response_model=PostResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create_postal_office(current_user: User = Depends(auth_service.get_current_user),
                               db: Session = Depends(get_db)):
    """
    The create_postal_office function creates a new postal office for the current user.
    If the user already has a post, it will return an error.

    Args:
        current_user: User: Get the current user
        db: Session: Access the database

    Returns:
        A post object
    """
    post = await repository_posts.get_posts_by_user_id(current_user.id, db)

    if post:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    new_post = await repository_posts.create_postal_office(current_user, db)

    return new_post


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

    return {"message": "An address of ukr postal office from post deleted successfully"}

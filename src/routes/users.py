import logging

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import (
    UserResponse,
    UserChangeRole,
    UserUpdateData,
    UserResponseAfterUpdate,
    UserResponseForCRM,
    UserBlockOrRemoveModel,
    PasswordChangeModel,
    UserMessageResponse
)
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.password_utils import hash_password, verify_password
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex
from src.services.validation import validate_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/all_for_crm", response_model=list[UserResponseForCRM],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_all_users_for_crm(limit: int, offset: int, db: Session = Depends(get_db)):
    """
    The function returns a list of all users in the database.

    Args:
        limit: int: Limit the number of users returned
        offset: int: Specify the offset of the first user to be returned
        db: Session: Access the database

    Returns:
        A list of users
    """
    return await repository_users.get_all_users(limit, offset, db)


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        It requires authentication, and it uses the auth_service to get the current user.

    Arguments:
        current_user (User): the current user attempting to delete the comment

    Returns:
        User: The current user object
    """
    return current_user


@router.put("/change_role", response_model=UserChangeRole, dependencies=[Depends(allowed_operation_admin)])
async def change_role(body: UserChangeRole,
                      user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    Change the role of a user

    Arguments:
        body (UserChangeRole): object with new role
        user (User): the current user
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User: object after the change operation
    """
    user = await repository_users.change_role(body, user, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    return user


@router.put("/me/", response_model=UserResponseAfterUpdate)
async def update_current_user(
    user_data: UserUpdateData,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the data of the current_user

    Arguments:
        user_data (UserUpdateData): object with updated user data
        current_user (User): the current user
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User: object after the change operation
    """
    return await repository_users.update_user_data(db, user_data, current_user)


@router.put("/block_user",
            response_model=UserResponseForCRM,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def block_user(user: UserBlockOrRemoveModel, db: Session = Depends(get_db)):
    """
    The block_user function blocks a user.

    Args:
        user: UserBlockOrRemoveModel: Get the id of the user to block and changed status of field is_blocked
        db: Session: Access the database

    Returns:
        A user blocked model object
    """
    user = await repository_users.get_user_by_id(user.id, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    block_user_ = await repository_users.block_user(user.id, db)

    await delete_cache_in_redis()

    return block_user_


@router.put("/unblock_user",
            response_model=UserResponseForCRM,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def unblock_user(user: UserBlockOrRemoveModel, db: Session = Depends(get_db)):
    """
    The unblock_user function unblocks a user.

    Args:
        user: UserBlockOrRemoveModel: Get the id of the user to unblock and changed status of field is_blocked
        db: Session: Access the database

    Returns:
        A user unblocked model object
    """
    user = await repository_users.get_user_by_id(user.id, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if not user.is_blocked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    unblock_user_ = await repository_users.unblock_user(user.id, db)

    await delete_cache_in_redis()

    return unblock_user_


@router.put("/remove_user",
            response_model=UserResponseForCRM,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def remove_user(user: UserBlockOrRemoveModel, db: Session = Depends(get_db)):
    """
    The remove_user function deletes a user.

    Args:
        user: UserBlockOrRemoveModel: Get the id of the user to delete and changed status of field is_deleted
        db: Session: Access the database

    Returns:
        A user deleted model object
    """
    user = await repository_users.get_user_by_id(user.id, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if not user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Ex.HTTP_403_FORBIDDEN)
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    delete_user = await repository_users.remove_user(user.id, db)

    await delete_cache_in_redis()

    return delete_user


@router.put("/return_user",
            response_model=UserResponseForCRM,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def return_user(user: UserBlockOrRemoveModel, db: Session = Depends(get_db)):
    """
    The return_user function returns a user.

    Args:
        user: UserBlockOrRemoveModel: Get the id of the user to return
        and changed status of fields is_deleted and is_blocked
        db: Session: Access the database

    Returns:
        A user returned model object
    """
    user = await repository_users.get_user_by_id(user.id, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if not user.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    return_user_ = await repository_users.return_user(user.id, db)

    await delete_cache_in_redis()

    return return_user_


@router.post("/me/change_password", response_model=UserMessageResponse)
async def change_password(
    body: PasswordChangeModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    The change_password function takes a body as input.
    The body contains the new password for that user, which is hashed using pwd_context.hash() before being stored in
    the database.

    Args:
        body: PasswordChangeModel: Get the password from the request body
        db: Session: Get the database session
        current_user (User): the current user

    Returns:
        A message to the user
    """
    user = await repository_users.get_user_by_email(current_user.email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST
        )

    if not verify_password(body.old_password, user.password_checksum):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )

    try:
        validate_password(body.new_password)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    if body.new_password != body.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The new password and new password confirm must be equal!"
        )

    body.new_password = hash_password(body.new_password)
    await repository_users.change_password(user.email, body.new_password, db)

    return {"message": "Your Password changed successfully!"}

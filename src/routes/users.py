from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role, BlacklistToken
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserResponse, UserChangeRole  # UserUpdate, UserUpdateAdmin, UserShow
from src.services.roles import RoleAccess

router = APIRouter(prefix="/users", tags=["users"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])


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
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return user

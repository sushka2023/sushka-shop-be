from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User, BlacklistToken
from src.schemas.users import UserModel, UserChangeRole, UserUpdateData

from src.repository import baskets as repository_baskets
from src.repository import favorites as repository_favorites
from src.repository import posts as repository_posts

from src.services.exception_detail import ExDetail as Ex

from src.services.password_utils import hash_password


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    Arguments:
        email (str): Pass in the email of the user we want to find
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User | None: A user object or None if the user is not found
    """
    return db.query(User).filter_by(email=email).first()


async def get_user_by_id(user_id: int, db: Session) -> User | None:
    """
    Function takes a user_id and a database session,
    and returns the user with that id if it exists. If no such user exists,
    it returns None.

    Arguments:
        user_id (int): Pass in the id of the user we want to find
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User | None: A user object or None if the user is not found
    """
    return db.query(User).filter_by(id=user_id).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.

    Arguments:
        body (UserModel): Pass in the UserModel object that is created from the request body
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User: A user object, which is the same as what we return from our get_user function
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def change_role(body: UserChangeRole, user: User, db: Session) -> User | None:
    """
    Logged-in admin can change role of any profile by ID.

    Arguments:
        body (UserChangeRole): A set of user new role
        user (User): the current user
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User | None: A user object or None
    """
    user_to_update = db.query(User).filter(User.id == body.id).first()
    if user_to_update:
        user_to_update.role = body.role
        user_to_update.updated_at = datetime.now()
        db.commit()
        return user_to_update
    return None


async def update_token(user: User, refresh_token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    Arguments:
        user (User): Pass the user object to the function
        refresh_token (str | None): Pass the refresh token to the update_token function
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        None
    """
    user.refresh_token = refresh_token
    db.commit()


async def is_blacklisted_token(token: str, db: Session) -> bool:
    """
    Function takes checks if a token is blacklisted.

    Arguments:
        token (str): token to be checked
        db (Session): SQLAlchemy session object for accessing the database
    Returns:
        bool
    """
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    if blacklist_token:
        return True
    return False


async def add_to_blacklist(token: str, db: Session) -> None:
    """
    Function adds a token to the blacklist.

    Arguments:
        token (str): The JWT that is being blacklisted.
        db (Session): SQLAlchemy session object for accessing the database
    Returns:
        None
    """
    blacklist_token = BlacklistToken(token=token, added_on=datetime.now())
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)
    return None


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.is_active = True
    db.commit()


async def reset_password(email: str, password: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.password_checksum = password
    db.commit()


async def update_user_data(db: Session, user_data: UserUpdateData, user: User) -> User:
    """
    Function updates the user data.

    Arguments:
        user_data (UserUpdateData): object with updated user data
        user (User): the current user
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        User: current user with updated data
    """
    updated_data_user = await get_user_by_id(user_id=user.id, db=db)

    updated_data_user.update_from_dict(user_data.dict())
    updated_data_user.updated_at = datetime.now()

    db.commit()
    db.refresh(updated_data_user)

    return updated_data_user


async def get_all_users(limit: int, offset: int, db: Session) -> list[User]:
    """
    Function takes a database session, and returns the user data if it exists.
    If no such users exists, it returns an empty list.

    Arguments:
        limit: int: Limit the number of users returned
        offset: int: Specify the offset of the first user to be returned
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        list[User] : a list of users or an empty list if the users is not found
    """
    users = (
        db.query(User).order_by(User.is_blocked, User.is_deleted)
        .order_by(User.id).limit(limit).offset(offset).all()
    )
    return users


async def block_user(user_id: int, db: Session) -> User | None:
    user = await get_user_by_id(user_id=user_id, db=db)
    if user and not user.is_blocked:
        user.is_blocked = True
        db.commit()
        return user
    return None


async def unblock_user(user_id: int, db: Session) -> User | None:
    user = await get_user_by_id(user_id=user_id, db=db)
    if user and user.is_blocked:
        user.is_blocked = False
        db.commit()
        return user
    return None


async def remove_user(user_id: int, db: Session) -> User | None:
    user = await get_user_by_id(user_id=user_id, db=db)
    if user and user.is_blocked and not user.is_deleted:
        user.is_deleted = True
        db.commit()
        return user
    return None


async def return_user(user_id: int, db: Session) -> User | None:
    user = await get_user_by_id(user_id=user_id, db=db)
    if user and user.is_blocked and user.is_deleted:
        user.is_deleted = False
        user.is_blocked = False
        db.commit()
        return user
    return None


async def change_password(email: str, password: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.password_checksum = password
    db.commit()


async def create_account_anonym_user(
        email: str, password: str, first_name: str, last_name: str, db: Session
) -> User:
    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_checksum=password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    favorite = await repository_favorites.favorites(new_user, db)
    if favorite:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    await repository_favorites.create(new_user, db)  # New favorite in user

    basket = await repository_baskets.baskets(new_user, db)
    if basket:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    await repository_baskets.create(new_user, db)  # New basket in user

    post = await repository_posts.get_posts_by_user_id(new_user.id, db)
    if post:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    await repository_posts.create_postal_office(new_user, db)  # New post in user

    return new_user

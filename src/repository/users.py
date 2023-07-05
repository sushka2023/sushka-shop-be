from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import User, BlacklistToken
from src.schemas.users import UserModel, UserChangeRole
from src.services.auth import auth_service


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

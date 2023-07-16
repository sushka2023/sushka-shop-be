from fastapi import Depends, HTTPException, status, APIRouter, Security, Request, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.email import RequestEmail
from src.schemas.users import UserModel, UserResponse, TokenModel, PasswordModel
from src.repository import favorites as repository_favorites
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_email
from src.services.exception_detail import ExDetail as Ex


router = APIRouter(prefix="/auth", tags=['auth'])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    body.password_checksum = auth_service.pwd_context.hash(body.password_checksum)
    new_user = await repository_users.create_user(body, db)  # New user

    favorite = await repository_favorites.favorites(new_user, db)
    if favorite:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    await repository_favorites.create(new_user, db)  # New favorite in user

    background_tasks.add_task(send_email, new_user.email, new_user.first_name, request.base_url)  # Send email verefication user
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes the username and password from the request body,
        verifies them against the database, and returns an access token if successful.

    Arguments:
        body (OAuth2PasswordRequestForm): Get the token from the request header
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        dict: JSON access_token / refresh_token / token_type
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Ex.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Ex.HTTP_403_FORBIDDEN)
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Ex.HTTP_403_FORBIDDEN)
    if not auth_service.pwd_context.verify(body.password, user.password_checksum):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Ex.HTTP_401_UNAUTHORIZED)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Security(security),
                 db: Session = Depends(get_db),
                 current_user: UserModel = Depends(auth_service.get_current_user)):
    """
    The logout function is used to logout a user.
    It takes the credentials,
    add access token to blacklist, and returns massage.

    Arguments:
        credentials (HTTPAuthorizationCredentials): Get the token from the request header
        db (Session): SQLAlchemy session object for accessing the database
        current_user (UserModel): the current user

    Returns:
        dict: JSON message
    """
    token = credentials.credentials

    await repository_users.add_to_blacklist(token, db)
    return {"message": "USER_IS_LOGOUT"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
        If the user's current refresh_token does not match what was
            passed into this function then it will return an error.

    Arguments:
        credentials (HTTPAuthorizationCredentials): Get the token from the request header
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        dict: JSON access_token - refresh_token - token_type
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)
    if user.is_active:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)
    if user.is_active:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.get('/reset_password/{email}')
async def send_email_reset_password(email: str, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)
    if not user.is_active:
        return {"message": "Your email is not confirmed"}
    background_tasks.add_task(send_reset_email, user.email, request.base_url)
    return {"message": "Letter sent successfully"}


@router.post('/reset_password/confirmed/{token}')
async def reset_password(token: str, body: PasswordModel, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)
    if not user.is_active:
        return {"message": "Your email is not confirmed"}
    body.password_checksum = auth_service.pwd_context.hash(body.password_checksum)
    await repository_users.reset_password(email, body.password_checksum, db)
    return {"message": "Password changed"}

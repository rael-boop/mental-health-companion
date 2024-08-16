from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated

from src.models import DatabaseSession
from src.models.user import User
from src.schemas.user import UserPublicSchema
from src.schemas.token import TokenTypeEnum
from src.services.token import TokenCharacterType
from src.services.auth import AuthService
from src.services.token import (
    TokenBlacklistService, TokenService
)
from src.utils import AppUtils, CustomError
from src.utils.logger import logger
from src.middlewares.auth import ActiveUser
from src.services.mail import Emailer


auth_routes = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


# pydantic models
class LoginInput(BaseModel):
    email: str
    password: str


class RegisterInput(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


# auth views
@auth_routes.post("/login", status_code=status.HTTP_200_OK)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = AuthService.authenticate_user(
        form_data.username, form_data.password
    )

    if not user:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = AuthService.create_auth_tokens(user)
    logger.info(f"::>User login success:{form_data.username}")

    return AppUtils.create_response(
        message="Login Success",
        data={
            "tokens": tokens
        }
    )


@auth_routes.post("/register")
def register(input: RegisterInput):

    with DatabaseSession().withSession() as session:
        # Validate user does not exists
        normalized_email = input.email.strip().lower()
        user_orm = AuthService.get_user_by_email(normalized_email)

        if not user_orm:
            hashed_password = AuthService.make_hashed_password(input.password)
            user_orm = User(
                first_name=input.first_name,
                last_name=input.last_name,
                email=normalized_email,
                password=hashed_password
            )
            session.add(user_orm)
            session.commit()

            user = UserPublicSchema.from_orm(user_orm)
            tokens = AuthService.create_auth_tokens(user)

            # request email verify
            _request_email_verify(
                user_id=user_orm.id,
                email=user_orm.email
            )

            return AppUtils.create_response(
                message="User successfully created",
                data={
                    "user": user.model_dump(),
                    "tokens": tokens
                }
            )
        else:
            raise CustomError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )


class RefreshTokenInput(BaseModel):
    refresh_token: str


@auth_routes.post("/refresh")
def access_token_refresh(input: RefreshTokenInput):

    # check token blacklist
    if TokenBlacklistService.is_blacklisted(input.refresh_token):
        raise CustomError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    (valid, payload) = AuthService.verify_jwt_token(
        input.refresh_token, "refresh")

    if not valid:
        raise CustomError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("id")
    user = AuthService.get_user_by_id(user_id)
    access_token = AuthService.create_access_token(user)

    return AppUtils.create_response(
        message="Access token refresh",
        data={
            "tokens": {
                "access": access_token
            }
        }
    )


@auth_routes.post("/logout")
def logout(user: ActiveUser, input: RefreshTokenInput):

    if TokenBlacklistService.is_blacklisted(input.refresh_token):
        raise CustomError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    (valid, payload) = AuthService.verify_jwt_token(
        input.refresh_token, "refresh")

    if not valid:
        raise CustomError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    TokenBlacklistService.blacklist_token(input.refresh_token)
    return AppUtils.create_response(
        message="Logout successful",
    )


class EmailVerifyRequestInput(BaseModel):
    email: str


def _request_email_verify(user_id, email: str):

    (token_str, token) = TokenService.create_token_model(
        user_id=user_id,
        type=TokenTypeEnum.email_verify,
        token_character_type=TokenCharacterType.number,
        length=6,
        expiration_hours=72,
        encode_token=False
    )

    Emailer().send_email(
        recipient_email=email,
        message=f"Verify Your Email Now: {token_str}",
        subject="Mental Health Companion: Verify your email"
    )


@auth_routes.post("/email-verify/request")
def request_email_verify(input: EmailVerifyRequestInput):
    user = AuthService.get_user_by_email(input.email)

    if not user:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email does not exists"
        )

    if user.is_email_verified:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your email has already been verified"
        )

    _request_email_verify(
        user_id=user.id,
        email=input.email
    )
    return AppUtils.create_response(
        message="Instructions have been forwarded to your email"
    )


class EmailVerifyInput(BaseModel):
    token: str


@auth_routes.post("/email-verify")
def email_verify(user: ActiveUser, input: EmailVerifyInput):

    # verify tokens
    (exists, token) = TokenService.get_by_encoded_token(
        token=input.token,
        type=TokenTypeEnum.email_verify,
        is_encoded=False,
        user_id=user.id
    )

    if not token:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not exists"
        )

    # Verify user
    user = AuthService.get_user_by_id(token.user_id)
    if not user:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not exists"
        )

    # Update user
    with DatabaseSession().withSession() as session:
        user_orm = session.query(User).where(User.id == user.id).one()
        user_orm.is_email_verified = True
        session.add(user_orm)
        session.commit()

    # Delete token
    TokenService.delete_token(token.id)

    return AppUtils.create_response(
        message="Email verified successfully"
    )


class PasswordResetRequestInput(BaseModel):
    email: str


@auth_routes.post("/password-reset")
def request_password_reset(input: PasswordResetRequestInput):
    with DatabaseSession().withSession() as session:
        user_orm = session.query(User).where(User.email == input.email).one()

        (encoded_token_str, token) = TokenService.create_token_model(
            user_orm.id,
            type=TokenTypeEnum.password_reset,
            token_character_type=TokenCharacterType.number,
            length=6,
            expiration_hours=6,
            encode_token=False,
        )

        Emailer().send_email(
            recipient_email=user_orm.email,
            message=f"Reset your password now Now: {encoded_token_str}",
            subject="Mental Health Companion: Reset your password"
        )
        return AppUtils.create_response(
            message="Instructions sent"
        )


class PasswordResetConfirm(BaseModel):
    password: str
    token: str
    email: str


@auth_routes.post("/password-reset/confirm")
def password_reset(input: PasswordResetConfirm):

    user = AuthService.get_user_by_email(input.email)
    if not user:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exists"
        )

    (exists, token) = TokenService.get_by_encoded_token(
        token=input.token,
        type=TokenTypeEnum.password_reset,
        is_encoded=False,
        user_id=user.id
    )

    if not token:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not exists"
        )

    # Verify user
    user = AuthService.get_user_by_id(token.user_id)
    if not user:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not exists"
        )

    # Update user
    with DatabaseSession().withSession() as session:
        user_orm = session.query(User).where(User.id == user.id).one()
        hashed_password = AuthService.make_hashed_password(input.password)
        user_orm.password = hashed_password
        session.add(user_orm)
        session.commit()

    # Delete token
    TokenService.delete_token(token.id)
    return AppUtils.create_response(
        message="Password changed successfully"
    )

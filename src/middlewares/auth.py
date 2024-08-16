from typing import Annotated, Optional
from fastapi import Depends, status
from pydantic import BaseModel, Field

from src.services.auth import oauth2_scheme
from src.utils import CustomError
from src.services.auth import AuthService
from src.models.user import UserSchema


class TokenData(BaseModel):
    id: int | str = None


class MiddlewareOptions(BaseModel):
    requires_verified_email: Optional[bool] = Field(default=False)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = CustomError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = None
    (valid, payload) = AuthService.verify_jwt_token(token, "access")
    if not valid:
        raise credentials_exception

    id = payload.get("id")
    token_data = TokenData(id=id)

    user = AuthService.get_user_by_id(token_data.id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserSchema, Depends(get_current_user)]
):
    if not current_user.active:
        raise CustomError(
            detail="User is inactive",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return current_user


async def get_verified_user(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
):
    if not current_user.is_email_verified:
        raise CustomError(
            detail="Verify your email to continue",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return current_user


async def get_admin_user(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
):
    if not current_user.is_admin:
        raise CustomError(
            detail="Unauthorized, admin privileges required",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return current_user


ActiveUser = Annotated[UserSchema, Depends(get_current_active_user)]
VerifiedUser = Annotated[UserSchema, Depends(get_verified_user)]
AdminUser = Annotated[UserSchema, Depends(get_admin_user)]

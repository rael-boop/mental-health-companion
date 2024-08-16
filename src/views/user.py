from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.middlewares.auth import ActiveUser
from src.schemas.user import (
    UserPublicSchema
)
from src.models.user import User
from src.models import DatabaseSession
from src.utils import AppUtils

user_routes = APIRouter(
    prefix="/user",
    tags=['user']
)


@user_routes.get("/me")
def get_me(user: ActiveUser):
    public_user = UserPublicSchema(**user.dict())
    return AppUtils.create_response(
        message="User",
        data=public_user.model_dump()
    )


class UpdateUserInput(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


@user_routes.put("/me")
def update_me(user: ActiveUser, input: UpdateUserInput):
    with DatabaseSession().withSession() as session:

        # query user and perform update
        user_orm = session.query(User).where(User.id == user.id).one()
        user_orm.first_name = input.first_name
        user_orm.last_name = input.last_name
        session.add(user_orm)  # Add the updated user to the session
        session.commit()

        # load user
        user = UserPublicSchema.from_orm(user_orm)

    return AppUtils.create_response(
        message="User updated",
        data=user.model_dump()
    )

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='allow')
    id: int
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    is_email_verified: bool = Field(default=False)
    google_id: Optional[str] = Field(nullable=True, default=None)
    active: bool = Field(default=True)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)


class UserPublicSchema(UserSchema):
    id: int = Field(exclude=True)
    password: str = Field(nullable=False, exclude=True)

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum


class TokenBlacklistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='allow')
    id: int
    token: str
    expires_at: datetime = Field(nullable=True)


class TokenTypeEnum(Enum):
    email_verify = "email_verify",
    password_reset = "password_reset"


class TokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='allow')
    id: int
    token: str | int
    user_id: int
    type: TokenTypeEnum
    created_at: datetime = Field(
        nullable=False, default_factory=datetime.utcnow)
    expires_at: datetime = Field(nullable=True)

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Text, DateTime, TIMESTAMP, ForeignKey
from datetime import datetime
from sqlalchemy import Enum as SaEnum

from . import Base
from src.schemas.token import (
    TokenBlacklistSchema,
    TokenSchema,
    TokenTypeEnum
)


class TokenBlacklist(Base):
    __tablename__ = "token_blacklists"
    __pydantic_model__ = TokenBlacklistSchema
    token: Mapped[str] = mapped_column(Text, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<TokenBlacklist(token={self.token})>"


class Token(Base):
    __tablename__ = "tokens"
    __pydantic_model__ = TokenSchema

    token: Mapped[str] = mapped_column(Text, unique=True, index=True)
    type: Mapped[str] = mapped_column(SaEnum(TokenTypeEnum), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

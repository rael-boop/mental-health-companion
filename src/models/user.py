from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, TIMESTAMP, Text, Boolean
from datetime import datetime

from . import Base
from src.schemas.user import UserSchema


class User(Base):
    __tablename__ = "users"
    __pydantic_model__ = UserSchema
    first_name: Mapped[str] = mapped_column(String(40))
    last_name: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    google_id: Mapped[str] = mapped_column(String(30), nullable=True)
    password: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<User(email={self.email})>"

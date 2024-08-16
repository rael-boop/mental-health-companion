from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from sqlalchemy import (
    Text, DateTime, TIMESTAMP, String
)
from . import Base
from src.schemas.resource import (
    ResourceSchema
)


class Resource(Base):
    __tablename__ = "resources"
    __pydantic_model__ = ResourceSchema
    title: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    thumbnail_url: Mapped[str] = mapped_column(
        String(100), unique=True, index=True)
    video_url: Mapped[str] = mapped_column(
        String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Resource(title={self.title})>"

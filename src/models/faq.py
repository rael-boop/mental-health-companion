from sqlalchemy import (
    TIMESTAMP,
    String,
    Text
)
from sqlalchemy.orm import mapped_column, Mapped
from src.schemas.faq import FaqSchema
from datetime import datetime
from . import Base


class Faq(Base):
    __tablename__ = "faqs"
    __pydantic_model__ = FaqSchema

    question: Mapped[str] = mapped_column(String(200))
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Faq(question={self.question})>"

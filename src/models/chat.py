from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    String,
    Float,
    Text
)
from datetime import datetime

from . import Base
from src.schemas.chat import ChatSchema, PromptSchema, SentimentSchema


class Chat(Base):
    __tablename__ = "chats"
    __pydantic_model__ = ChatSchema
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True)
    owner: Mapped["User"] = relationship("User")
    title: Mapped[str] = mapped_column(String(40), nullable=False)
    prompts: Mapped[List["Prompt"]] = relationship()
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Chat(owner={self.owner})>"


class Prompt(Base):
    __tablename__ = "prompts"
    __pydantic_model__ = PromptSchema

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id"), nullable=True)
    chat: Mapped["Sentiment"] = relationship("Chat", back_populates="prompts")

    sentiments: Mapped[List["Sentiment"]] = relationship()

    prompt: Mapped[str] = mapped_column(Text)
    bot_response: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Prompt(prompt={self.prompt})>"


class Sentiment(Base):
    __tablename__ = "sentiments"
    __pydantic_model__ = SentimentSchema
    prompt_id: Mapped[int] = mapped_column(
        ForeignKey("prompts.id"), nullable=True)
    prompt: Mapped["Prompt"] = relationship(
        "Prompt", back_populates="sentiments")

    score: Mapped[int] = mapped_column(Float, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow)

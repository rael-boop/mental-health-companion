from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ChatSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='allow')
    id: int
    title: str
    owner_id: int = Field(nullable=False)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)


class PromptSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='allow')
    id: int
    chat_id: int = Field(nullable=False)
    prompt: str = Field(nullable=False)
    bot_response: str = Field(nullable=False)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)


class SentimentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='allow')
    id: int
    prompt_id: int = Field(nullable=False)
    score: float = Field(nullable=False)
    sentiment: str = Field(default=[])
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)

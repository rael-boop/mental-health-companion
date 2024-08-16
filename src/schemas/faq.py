from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class FaqSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: int
    question: str
    answer: str
    created_at: datetime = Field(
        nullable=False,
        default_factory=datetime.utcnow
    )

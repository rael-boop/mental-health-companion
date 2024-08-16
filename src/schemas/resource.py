from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ResourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: int
    title: str
    thumbnail_url: str
    description: str
    video_url: str
    created_at: datetime = Field(
        nullable=False,
        default_factory=datetime.utcnow
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=datetime.utcnow
    )

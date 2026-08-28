from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

MessageRole = Literal["user", "assistant", "system"]


class MessageRequest(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, max_length=100_000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

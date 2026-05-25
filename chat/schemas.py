from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatCreate(BaseModel):
    trainer_id: int

class ChatResponse(BaseModel):
    id: int
    client_id: int
    trainer_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    text: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
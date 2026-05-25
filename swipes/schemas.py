from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrainerRequestCreate(BaseModel):
    trainer_id: int
    message: Optional[str] = None

class TrainerRequestUpdate(BaseModel):
    status: str  # accepted / declined / cancelled

class TrainerRequestResponse(BaseModel):
    id: int
    client_id: int
    trainer_id: int
    status: str
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
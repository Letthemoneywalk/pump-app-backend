from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrainingCreate(BaseModel):
    title: str
    type: Optional[str] = None
    starts_at: datetime
    duration_minutes: Optional[int] = None
    format: Optional[str] = None
    notes: Optional[str] = None
    client_id: Optional[int] = None
    trainer_id: Optional[int] = None

class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    starts_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    format: Optional[str] = None
    notes: Optional[str] = None

class TrainingResponse(BaseModel):
    id: int
    client_id: Optional[int] = None
    trainer_id: Optional[int] = None
    title: str
    type: Optional[str] = None
    starts_at: datetime
    duration_minutes: Optional[int] = None
    status: str
    format: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
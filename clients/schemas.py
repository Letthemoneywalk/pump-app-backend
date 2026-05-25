from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClientProfileCreate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    goal: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    training_place: Optional[str] = None
    sessions_per_week: Optional[int] = None
    about: Optional[str] = None
    health_limitations: Optional[str] = None

class ClientProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    goal: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    training_place: Optional[str] = None
    sessions_per_week: Optional[int] = None
    about: Optional[str] = None
    health_limitations: Optional[str] = None

class ClientProfileResponse(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    goal: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    training_place: Optional[str] = None
    sessions_per_week: Optional[int] = None
    about: Optional[str] = None
    health_limitations: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
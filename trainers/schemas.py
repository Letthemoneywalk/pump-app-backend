from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrainerProfileCreate(BaseModel):
    bio: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    price: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    is_online_available: Optional[bool] = False

class TrainerProfileUpdate(BaseModel):
    bio: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    price: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    is_online_available: Optional[bool] = None

class TrainerProfileResponse(BaseModel):
    id: int
    user_id: int
    bio: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    price: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    is_online_available: Optional[bool] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_verified: Optional[bool] = None
    created_at: datetime

    model_config = {"from_attributes": True}
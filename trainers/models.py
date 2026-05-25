from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class TrainerProfile(Base):
    __tablename__ = "trainer_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    bio = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    is_online_available = Column(Boolean, default=False)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
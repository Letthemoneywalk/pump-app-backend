from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from users.models import User
from trainers.models import TrainerProfile
from trainers.schemas import TrainerProfileResponse, TrainerProfileCreate, TrainerProfileUpdate

router = APIRouter()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/feed", response_model=list[TrainerProfileResponse])
async def get_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(TrainerProfile))
    trainers = result.scalars().all()
    return trainers

@router.get("/{trainer_id}", response_model=TrainerProfileResponse)
async def get_trainer(
    trainer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TrainerProfile).where(TrainerProfile.id == trainer_id)
    )
    trainer = result.scalar_one_or_none()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer


@router.post("/profile", response_model=TrainerProfileResponse)
async def create_trainer_profile(
    profile_data: TrainerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Only trainers can create trainer profile")
    
    new_profile = TrainerProfile(
        user_id=current_user.id,
        bio=profile_data.bio,
        specialty=profile_data.specialty,
        experience_years=profile_data.experience_years,
        price=profile_data.price,
        gender=profile_data.gender,
        age=profile_data.age,
        location=profile_data.location,
        is_online_available=profile_data.is_online_available
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.routers.trainers import get_current_user
from users.models import User
from clients.models import ClientProfile
from clients.schemas import ClientProfileCreate, ClientProfileUpdate, ClientProfileResponse

router = APIRouter()

@router.post("/profile", response_model=ClientProfileResponse)
async def create_client_profile(
    profile_data: ClientProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create client profile")

    result = await db.execute(
        select(ClientProfile).where(ClientProfile.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    new_profile = ClientProfile(
        user_id=current_user.id,
        age=profile_data.age,
        gender=profile_data.gender,
        goal=profile_data.goal,
        budget_min=profile_data.budget_min,
        budget_max=profile_data.budget_max,
        training_place=profile_data.training_place,
        sessions_per_week=profile_data.sessions_per_week,
        about=profile_data.about,
        health_limitations=profile_data.health_limitations
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile

@router.get("/profile", response_model=ClientProfileResponse)
async def get_client_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ClientProfile).where(ClientProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.patch("/profile", response_model=ClientProfileResponse)
async def update_client_profile(
    update_data: ClientProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ClientProfile).where(ClientProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in update_data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile
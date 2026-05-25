from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.routers.trainers import get_current_user
from users.models import User
from scheduling.models import Training
from scheduling.schemas import TrainingCreate, TrainingUpdate, TrainingResponse

router = APIRouter()

@router.post("/", response_model=TrainingResponse)
async def create_training(
    training_data: TrainingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # определяем пару клиент+тренер
    if current_user.role == "client":
        client_id = current_user.id
        trainer_id = training_data.trainer_id
    else:
        trainer_id = current_user.id
        client_id = training_data.client_id

    # оба должны быть указаны
    if not client_id or not trainer_id:
        raise HTTPException(
            status_code=400,
            detail="Both client_id and trainer_id are required"
        )

    # проверяем что тренировка на это время уже не существует
    result = await db.execute(
        select(Training).where(
            Training.client_id == client_id,
            Training.trainer_id == trainer_id,
            Training.starts_at == training_data.starts_at,
            Training.status != "cancelled"
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Training already exists at this time"
        )

    new_training = Training(
        title=training_data.title,
        type=training_data.type,
        starts_at=training_data.starts_at,
        duration_minutes=training_data.duration_minutes,
        format=training_data.format,
        notes=training_data.notes,
        client_id=client_id,
        trainer_id=trainer_id,
    )
    db.add(new_training)
    await db.commit()
    await db.refresh(new_training)
    return new_training

@router.get("/", response_model=list[TrainingResponse])
async def get_trainings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Training).where(
            or_(
                Training.client_id == current_user.id,
                Training.trainer_id == current_user.id
            )
        )
    )
    return result.scalars().all()

@router.patch("/{training_id}", response_model=TrainingResponse)
async def update_training(
    training_id: int,
    update_data: TrainingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Training).where(Training.id == training_id)
    )
    training = result.scalar_one_or_none()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    if training.client_id != current_user.id and training.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your training")

    for field, value in update_data.model_dump(exclude_none=True).items():
        setattr(training, field, value)

    await db.commit()
    await db.refresh(training)
    return training

@router.delete("/{training_id}")
async def delete_training(
    training_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Training).where(Training.id == training_id)
    )
    training = result.scalar_one_or_none()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    if training.client_id != current_user.id and training.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your training")

    await db.delete(training)
    await db.commit()
    return {"status": "deleted"}
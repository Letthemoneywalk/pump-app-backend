from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
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
    from swipes.models import TrainerRequest

    if current_user.role == "client":
        client_id = current_user.id
        trainer_id = training_data.trainer_id
    else:
        trainer_id = current_user.id
        client_id = training_data.client_id
        if not client_id:
            raise HTTPException(
                status_code=422,
                detail="client_id is required for trainer"
            )

    # проверяем что между клиентом и тренером есть принятая заявка
    if client_id and trainer_id:
        result = await db.execute(
            select(TrainerRequest).where(
                TrainerRequest.client_id == client_id,
                TrainerRequest.trainer_id == trainer_id,
                TrainerRequest.status == "accepted"
            )
        )
        match = result.scalar_one_or_none()
        if not match:
            raise HTTPException(
                status_code=403,
                detail="No accepted request between this client and trainer"
            )
        # запрет тренировок в прошлом
    now = datetime.now(timezone.utc)
    starts_at = training_data.starts_at
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)
    if starts_at < now:
        raise HTTPException(
            status_code=400,
            detail="Cannot create training in the past"
        )

    # проверка пересечения интервалов
    if client_id and trainer_id:
        duration = training_data.duration_minutes or 60
        end_time = starts_at + timedelta(minutes=duration)
        result = await db.execute(
            select(Training).where(
                and_(
                    or_(
                        Training.client_id == client_id,
                        Training.trainer_id == trainer_id
                    ),
                    Training.status != "cancelled",
                    Training.starts_at < end_time,
                    Training.starts_at > starts_at - timedelta(hours=4)
                )
            )
        )
        overlap = result.scalar_one_or_none()
        if overlap:
            raise HTTPException(
                status_code=400,
                detail="Training overlaps with existing one"
            )

    # проверяем дубликат
    if client_id and trainer_id:
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
    limit: int = 20,
    offset: int = 0,
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
        .order_by(Training.starts_at.asc())
        .limit(limit)
        .offset(offset)
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
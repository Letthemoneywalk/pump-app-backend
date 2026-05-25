from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.routers.trainers import get_current_user
from users.models import User
from swipes.models import TrainerRequest
from swipes.schemas import TrainerRequestCreate, TrainerRequestUpdate, TrainerRequestResponse

router = APIRouter()

# клиент свайпает тренера вправо
@router.post("", response_model=TrainerRequestResponse)
async def create_request(
    request_data: TrainerRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can send requests")

    # проверяем что такой запрос уже не существует
    result = await db.execute(
        select(TrainerRequest).where(
            TrainerRequest.client_id == current_user.id,
            TrainerRequest.trainer_id == request_data.trainer_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Request already exists")

    new_request = TrainerRequest(
        client_id=current_user.id,
        trainer_id=request_data.trainer_id,
        message=request_data.message
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request

# тренер видит входящие заявки
@router.get("/incoming", response_model=list[TrainerRequestResponse])
async def get_incoming_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Only trainers can view incoming requests")

    result = await db.execute(
        select(TrainerRequest).where(TrainerRequest.trainer_id == current_user.id)
    )
    return result.scalars().all()

# тренер принимает или отклоняет заявку
@router.patch("/{request_id}", response_model=TrainerRequestResponse)
async def update_request(
    request_id: int,
    update_data: TrainerRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TrainerRequest).where(TrainerRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your request")

    request.status = update_data.status
    await db.commit()
    await db.refresh(request)
    return request
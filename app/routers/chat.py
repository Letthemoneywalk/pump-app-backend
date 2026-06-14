from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, AsyncSessionLocal
from app.routers.trainers import get_current_user
from app.auth import decode_access_token
from users.models import User
from chat.models import Chat, Message
from chat.schemas import ChatCreate, ChatResponse, MessageResponse


router = APIRouter()

# хранит активные подключения: chat_id → список websocket-ов
active_connections: dict[int, list[WebSocket]] = {}

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create chats")

    # проверяем что чат уже не существует
    result = await db.execute(
        select(Chat).where(
            Chat.client_id == current_user.id,
            Chat.trainer_id == chat_data.trainer_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    new_chat = Chat(
        client_id=current_user.id,
        trainer_id=chat_data.trainer_id
    )
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat

@router.get("/", response_model=list[ChatResponse])
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import or_
    result = await db.execute(
        select(Chat).where(
            or_(
                Chat.client_id == current_user.id,
                Chat.trainer_id == current_user.id
            )
        )
    )
    return result.scalars().all()

@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.client_id != current_user.id and chat.trainer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your chat")

    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, token: str):
    import json

    # проверяем токен
    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=1008)
        return

    # подключаем
    await websocket.accept()
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    try:
        while True:
            text = await websocket.receive_text()

            # сохраняем в базу
            async with AsyncSessionLocal() as db:
                new_message = Message(
                    chat_id=chat_id,
                    sender_id=user_id,
                    text=text
                )
                db.add(new_message)
                await db.commit()
                await db.refresh(new_message)

            # отправляем всем в этом чате
            payload = json.dumps({
                "type": "message",
                "message": {
                    "id": new_message.id,
                    "chat_id": chat_id,
                    "sender_id": user_id,
                    "text": text,
                    "created_at": new_message.created_at.isoformat() + "Z"
                }
            })

            dead_connections = []
            for connection in active_connections[chat_id]:
                try:
                    await connection.send_text(payload)
                except Exception:
                    dead_connections.append(connection)

            # удаляем мёртвые соединения
            for dead in dead_connections:
                active_connections[chat_id].remove(dead)

    except WebSocketDisconnect:
        if websocket in active_connections.get(chat_id, []):
            active_connections[chat_id].remove(websocket)
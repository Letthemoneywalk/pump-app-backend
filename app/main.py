from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.trainers import router as trainers_router
from app.routers.swipes import router as swipes_router
from app.routers.clients import router as clients_router
from app.routers.scheduling import router as scheduling_router
from app.routers.chat import router as chat_router

app = FastAPI(
    title="FitCoach API",
    description="Backend for trainer matching app",
    version="0.1.0"
)

app.router.redirect_slashes = False  # добавь эту строку

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(trainers_router, prefix="/trainers", tags=["trainers"])
app.include_router(swipes_router, prefix="/swipes", tags=["swipes"])
app.include_router(clients_router, prefix="/clients", tags=["clients"])
app.include_router(scheduling_router, prefix="/scheduling", tags=["scheduling"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])

@app.get("/health")
async def health():
    return {"status": "ok"}
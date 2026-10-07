from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import competitors, runs, workspace
from app.api.deps import ensure_default_workspace
from app.config import settings
from app.db import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with SessionLocal() as session:
        await ensure_default_workspace(session)
    yield


app = FastAPI(title="Competitor Pulse", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v1")
api.include_router(workspace.router)
api.include_router(competitors.router)
api.include_router(runs.router)
app.include_router(api)


@app.get("/health")
async def health():
    return {"status": "ok"}

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import competitors, discovery, runs, workspace
from app.config import settings
from app.db import SessionLocal
from app.mcp_server import mcp
from app.services.errors import Conflict, NotFound, ReadOnly, ServiceError
from app.services.workspaces import ensure_default_workspace

ERROR_STATUS = {
    NotFound: status.HTTP_404_NOT_FOUND,
    Conflict: status.HTTP_409_CONFLICT,
    ReadOnly: status.HTTP_403_FORBIDDEN,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with SessionLocal() as session:
        await ensure_default_workspace(session)
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Competitor Pulse", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    status_code = next(code for cls, code in ERROR_STATUS.items() if isinstance(exc, cls))
    return JSONResponse({"detail": str(exc)}, status_code=status_code)


api = APIRouter(prefix="/api/v1")
api.include_router(workspace.router)
for router in (workspace.scoped_router, competitors.router, runs.router, discovery.router):
    api.include_router(router, prefix="/workspaces/{workspace_id}")
app.include_router(api)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serves /mcp for outside agents (see docs/mcp.md). Mounted last so it only gets unmatched paths.
app.mount("/", mcp.streamable_http_app(stateless_http=True, json_response=True))

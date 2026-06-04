"""SecAgentX FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION, CORS_ORIGINS
from app.db.base import Base
from app.db.session import engine
from app.api import alerts, incidents, agents, evidence, actions, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)
app.include_router(incidents.router)
app.include_router(agents.router)
app.include_router(evidence.router)
app.include_router(actions.router)
app.include_router(reports.router)


@app.get("/api/health")
def health():
    return {"ok": True, "app": APP_NAME, "version": APP_VERSION}

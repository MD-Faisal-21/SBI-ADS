from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.dashboard import router as dashboard_router
from backend.decision import router as decision_router
from backend.forecast import router as forecast_router
from backend.inventory import router as inventory_router
from backend.model_performance import router as model_performance_router
from backend.system import router as system_router
from backend.upload import router as upload_router
from core import config
from database.connection import initialise_schema

config.ensure_directories()


@asynccontextmanager
async def lifespan(_: FastAPI):
    config.ensure_directories()
    initialise_schema()
    yield

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/charts",
    StaticFiles(directory=str(config.CHART_DIR)),
    name="charts",
)

app.mount(
    "/frontend",
    StaticFiles(directory=str(config.FRONTEND_DIR)),
    name="frontend",
)


@app.get("/", include_in_schema=False)
async def root():

    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", include_in_schema=False)
async def dashboard_page():

    return FileResponse(str(config.FRONTEND_DIR / "index.html"))


@app.get("/health", include_in_schema=False)
async def legacy_health():

    return {"status": "ok", "app": config.APP_NAME, "version": config.APP_VERSION}

for router in (
    upload_router,
    dashboard_router,
    forecast_router,
    decision_router,
    model_performance_router,
    inventory_router,
    system_router,
):

    app.include_router(router, prefix="/api")

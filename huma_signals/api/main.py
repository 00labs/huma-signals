import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from huma_signals.settings import settings

from .views import router as api_router

logger = structlog.get_logger(__name__)

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.env,
    traces_sample_rate=1.0,
)

app = FastAPI()

# for javascript to call the endpoints
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="", tags=["huma_signals"])


@app.get("/health")
async def get_health():
    return {"ok"}

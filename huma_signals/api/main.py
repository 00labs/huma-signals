import fastapi
import sentry_sdk
import structlog
from fastapi.middleware import cors

from huma_signals.api import views
from huma_signals.settings import settings

logger = structlog.get_logger(__name__)

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.env,
    traces_sample_rate=1.0,
)

app = fastapi.FastAPI()

# for javascript to call the endpoints
origins = ["*"]
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(views.router, prefix="", tags=["huma_signals"])


@app.get("/health")
async def get_health() -> str:
    return "ok"

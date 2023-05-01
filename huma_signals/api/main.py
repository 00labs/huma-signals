import datadog
import fastapi
import structlog
from ddtrace import opentracer
from fastapi.middleware import cors

from huma_signals.api import views
from huma_signals.settings import settings

logger = structlog.get_logger(__name__)

_DATADOG_HOST = "0.0.0.0"

if settings.instrumentation_enabled:
    datadog.initialize(
        api_key=settings.datadog_api_key,
        statsd_host=_DATADOG_HOST,
        statsd_port=8125,
    )
    tracer = opentracer.Tracer(
        "",
        config={
            "agent_hostname": _DATADOG_HOST,
            "agent_port": 8126,
        },
    )
    opentracer.set_global_tracer(tracer)

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

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .views import router as api_router

logger = structlog.get_logger(__name__)


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

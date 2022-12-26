from typing import Any, Dict

import structlog
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from huma_signals.adapters.models import SignalAdapterBase
from huma_signals.adapters.registry import ADAPTER_REGISTRY, fetch_signal

from .models import SignalFetchRequest, SignalFetchResponse

logger = structlog.get_logger(__name__)

router = APIRouter()


def _list_adapters(registry: Dict[str, SignalAdapterBase]) -> Dict[str, Any]:
    definition = {"adapters": [adapter.defintion() for adapter in registry.values()]}
    return jsonable_encoder(definition)


@router.get("/list_adapters", response_model=Dict)
def get_list_adapters():
    logger.info("Received list adapters request")
    return _list_adapters(ADAPTER_REGISTRY)


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


@router.post("/fetch", response_model=SignalFetchResponse)
def post_fetch(signal_request: SignalFetchRequest):
    logger.info("Received signal request", request=signal_request)
    signals = fetch_signal(signal_request.signal_names, signal_request.adapter_inputs)
    return jsonable_encoder(SignalFetchResponse(signals=signals))

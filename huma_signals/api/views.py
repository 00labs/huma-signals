from typing import Any, Dict, Type

import fastapi
import structlog
from fastapi import encoders

from huma_signals.adapters import models as adapter_models
from huma_signals.adapters import registry
from huma_signals.api import models

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


def _list_adapters(
    registry_: Dict[str, Type[adapter_models.SignalAdapterBase]]
) -> Dict[str, Any]:
    definition = {"adapters": [adapter.definition() for adapter in registry_.values()]}
    return encoders.jsonable_encoder(definition)


@router.get("/list_adapters", response_model=Dict)
async def get_list_adapters() -> Dict[str, Any]:
    logger.info("Received list adapters request")
    return _list_adapters(registry.ADAPTER_REGISTRY)


@router.post("/fetch", response_model=models.SignalFetchResponse)
async def post_fetch(signal_request: models.SignalFetchRequest) -> Dict[str, Any]:
    logger.info("Received signal request", request=signal_request)
    signals = await registry.fetch_signal(
        signal_request.signal_names, signal_request.adapter_inputs
    )
    return encoders.jsonable_encoder(models.SignalFetchResponse(signals=signals))

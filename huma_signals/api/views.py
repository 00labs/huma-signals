from typing import Any, Type

import fastapi
import structlog

from huma_signals.api import exception_handlers, models
from huma_signals.domain.adapters import models as adapter_models
from huma_signals.domain.adapters import registry

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


def _list_adapters(
    registry_: dict[str, Type[adapter_models.SignalAdapterBase]]
) -> dict[str, Any]:
    return {"adapters": [adapter.definition() for adapter in registry_.values()]}


@router.get("/list_adapters")
@exception_handlers.handle_exception
async def get_list_adapters() -> dict[str, Any]:
    logger.info("Received list adapters request")
    return _list_adapters(registry.ADAPTER_REGISTRY)


@router.post("/fetch")
@exception_handlers.handle_exception
async def fetch(
    signal_request: models.SignalFetchRequest,
) -> models.SignalFetchResponse:
    logger.info("Received signal request", request=signal_request)
    signals = await registry.fetch_signal(
        signal_request.signal_names, signal_request.adapter_inputs
    )
    return models.SignalFetchResponse(signals=signals)

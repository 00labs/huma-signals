from typing import Any, Dict, List, Type

import fastapi
import structlog
from fastapi import encoders

from huma_signals import constants
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters import registry
from huma_signals.adapters.banking import plaid_client
from huma_signals.api import models
from huma_signals.settings import settings

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


@router.get("/user-input-types", response_model=models.UserInputTypesResponse)
async def get_user_input_types(
    request: models.UserInputTypesRequest,
) -> List[constants.UserInputType]:
    logger.info("Received user input types request", request=request)
    user_input_types = await registry.fetch_user_input_types(
        signal_names=request.signal_names
    )
    return encoders.jsonable_encoder(
        models.UserInputTypesResponse(user_input_types=user_input_types)
    )


@router.post(
    "/create-plaid-link-token", response_model=models.CreatePlaidLinkTokenResponse
)
async def post_create_plaid_link_token(
    request: models.CreatePlaidLinkTokenRequest,
) -> List[constants.UserInputType]:
    logger.info("Received create plaid link token request", request=request)
    client = plaid_client.PlaidClient(
        plaid_env=settings.plaid_env,
        plaid_client_id=settings.plaid_client_id,
        plaid_secret=settings.plaid_secret,
    )
    link_token, user_token = await client.create_link_token(
        wallet_address=request.borrower_wallet_address
    )
    return encoders.jsonable_encoder(
        models.CreatePlaidLinkTokenResponse(
            link_token=link_token, user_token=user_token
        )
    )


@router.post("/fetch", response_model=models.SignalFetchResponse)
async def post_fetch(signal_request: models.SignalFetchRequest) -> Dict[str, Any]:
    logger.info("Received signal request", request=signal_request)
    signals = await registry.fetch_signal(
        signal_request.signal_names, signal_request.adapter_inputs
    )
    return encoders.jsonable_encoder(models.SignalFetchResponse(signals=signals))

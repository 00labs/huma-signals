# pylint: disable=too-few-public-methods
from typing import Any, Dict, List

import pydantic

from huma_signals import constants, models


class UserInputTypesRequest(models.HumaBaseModel):
    signal_names: List[str]


class UserInputTypesResponse(models.HumaBaseModel):
    user_input_types: List[constants.UserInputType]


class CreatePlaidLinkTokenRequest(models.HumaBaseModel):
    borrower_wallet_address: str = pydantic.Field(alias="borrowerWalletAddress")


class CreatePlaidLinkTokenResponse(models.HumaBaseModel):
    link_token: str = pydantic.Field(alias="linkToken")
    user_token: str = pydantic.Field(alias="userToken")


class SignalFetchRequest(models.HumaBaseModel):
    signal_names: List[str]
    adapter_inputs: Dict[str, Any]


class SignalFetchResponse(models.HumaBaseModel):
    signals: Dict[str, Any]

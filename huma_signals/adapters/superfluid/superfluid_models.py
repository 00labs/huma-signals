import pydantic
from huma_utils import pydantic_utils

from huma_signals import models


class SuperfluidSignals(models.HumaBaseModel):
    current_flow_rate: int = pydantic.Field(
        description="The current flow rate of the stream in the unit of wei/sec"
    )
    stream_id: str = pydantic.Field(description="The stream ID")


class SuperfluidStream(pydantic_utils.CamelCaseAliased):
    id: str
    updated_at_timestamp: int
    created_at_timestamp: int
    current_flow_rate: int

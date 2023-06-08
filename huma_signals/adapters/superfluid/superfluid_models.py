import pydantic

from huma_signals import models
from huma_signals.commons import pydantic_utils


class SuperfluidSignals(models.HumaBaseModel):
    current_flow_rate: int = pydantic.Field(
        description="The current flow rate of the stream in the unit of wei/sec"
    )


class SuperfluidStream(pydantic_utils.CamelCaseAliased):
    id: str
    updated_at_timestamp: int
    created_at_timestamp: int
    current_flow_rate: int

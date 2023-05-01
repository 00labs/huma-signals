import pydantic

from huma_signals.commons import string_utils


class CamelCaseAliased(pydantic.BaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = string_utils.snake_to_camel

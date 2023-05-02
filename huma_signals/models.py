# pylint: disable=too-few-public-methods

import pydantic


class HumaBaseModel(pydantic.BaseModel):
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        underscore_attrs_are_private = True

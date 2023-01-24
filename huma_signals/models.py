# pylint: disable=too-few-public-methods
import datetime
import decimal

import pydantic


class HumaBaseModel(pydantic.BaseModel):
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True
        allow_population_by_field_name = True
        underscore_attrs_are_private = True

        json_encoders = {
            # custom output conversion for datetime
            datetime.datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")
            if v
            else None,
            decimal.Decimal: lambda v: str(v) if v else None,
        }

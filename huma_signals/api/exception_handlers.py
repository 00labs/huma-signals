import functools
from typing import Any, Callable, Type

import fastapi
import structlog

from huma_signals import exceptions

logger = structlog.get_logger(__name__)


def handle_exception(f: Callable) -> Callable:
    @functools.wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await f(*args, **kwargs)
        except exceptions.HumaSignalException as e:
            logger.exception(f"Error calling {f}", error_message=e.message)
            status_code = _EXCEPTIONS_TO_HTTP_STATUS_CODES.get(type(e), 500)
            raise fastapi.HTTPException(
                status_code=status_code,
                detail={"type": e.__class__.__name__, "message": e.message},
            )
        except Exception as e:
            logger.exception(f"Error calling {f}", e=e)
            raise fastapi.HTTPException(
                status_code=500,
                detail={"type": e.__class__.__name__, "message": str(e)},
            )

    return wrapper


_EXCEPTIONS_TO_HTTP_STATUS_CODES: dict[Type[exceptions.HumaSignalException], int] = {
    exceptions.InvalidAddressException: 400,
    exceptions.PoolSettingsNotFoundException: 404,
}

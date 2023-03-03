import asyncio
import functools
from typing import Any, Callable


async def sync_to_async(f: Callable, *args: Any, **kwargs: Any) -> Any:
    event_loop = asyncio.get_event_loop()
    return await event_loop.run_in_executor(None, functools.partial(f, *args, **kwargs))

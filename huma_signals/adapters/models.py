from typing import Any


class SignalAdapterBase:
    async def fetch(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

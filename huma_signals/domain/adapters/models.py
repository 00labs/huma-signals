from typing import Any, ClassVar


class SignalAdapterBase:
    # Signal adapters name.
    name: ClassVar[str]
    # Signals that the adapter can fetch.
    signals: ClassVar[list[str]]
    # Inputs that the adapter requires.
    required_inputs: ClassVar[list[str]]

    @classmethod
    def definition(cls) -> dict[str, str | list[str]]:
        return {
            "name": cls.name,
            "signals": cls.signals,
            "required_inputs": cls.required_inputs,
        }

    async def fetch(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

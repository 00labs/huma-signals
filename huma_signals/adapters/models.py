from typing import Any, ClassVar, Dict, List


class SignalAdapterBase:
    # Signal adapters name.
    name: ClassVar[str]
    # Signals that the adapter can fetch
    signals: ClassVar[List[str]]
    # Inputs that the adapter requires
    required_inputs: ClassVar[List[str]]

    @classmethod
    def definition(cls) -> Dict[str, str | List[str]]:
        return {
            "name": cls.name,
            "signals": cls.signals,
            "required_inputs": cls.required_inputs,
        }

    async def fetch(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

from typing import Any, ClassVar, Dict, List

import pydantic

from huma_signals import constants


class SignalAdapterBase:
    name: ClassVar[str] = pydantic.Field(..., description="Signal Adapter's name")
    signals: ClassVar[List[str]] = pydantic.Field(
        ..., description="Signals that the adapter can fetch"
    )
    required_inputs: ClassVar[List[str]] = pydantic.Field(
        ..., description="Inputs that the adapter requires"
    )

    @classmethod
    def definition(cls) -> Dict[str, str | List[str]]:
        return {
            "name": cls.name,
            "signals": cls.signals,
            "required_inputs": cls.required_inputs,
        }

    async def fetch(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @classmethod
    def user_input_types(cls) -> List[constants.UserInputType]:
        """
        Returns the types of user inputs needed for fetching signals and the data
        needed to initialize them.

        The reason that this function exists is that some signals need additional data
        from the user on top of wallet addresses, e.g. in order to get banking signals
        we would need the user to link their bank account through Plaid on the UI, and
        the UI would need to understand what kind of components to launch in order to
        capture the user inputs.
        """
        return []

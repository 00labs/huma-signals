import pytest

from huma_signals.commons import chains, web3_utils
from huma_signals.settings import settings


def describe_get_w3() -> None:
    async def it_can_get_w3() -> None:
        w3 = await web3_utils.get_w3(settings.chain, settings.web3_provider_url)
        assert w3 is not None
        is_connected = await w3.is_connected()  # type: ignore[misc]
        assert is_connected is True

        # The type annotation for `eth` is wrong: it's annotated as `eth`, but it should be `AsyncEth`
        # in this case. If the type annotation is correct then it wouldn't complain about the presence of `await`.
        latest_block = await w3.eth.get_block("latest")  # type: ignore[misc]
        assert latest_block is not None
        assert latest_block["number"] > 0
        assert latest_block["hash"] is not None

        block = await w3.eth.get_block(latest_block["hash"])  # type: ignore[misc]
        assert block is not None
        assert block["number"] == latest_block["number"]

    async def it_raises_error_if_chain_is_not_matched_with_provider() -> None:
        with pytest.raises(ValueError):
            await web3_utils.get_w3(chains.Chain.POLYGON, settings.web3_provider_url)

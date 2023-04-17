import pytest

from huma_signals.adapters.allowlist import adapter
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/domain/adapters/allowlist"
# Don't match on path since the API key is embedded in the path.
_VCR_MATCH_ON = ["method", "scheme", "host", "port", "query"]


@pytest.fixture
def valid_address() -> str:
    return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0"


@pytest.fixture
def invalid_address() -> str:
    return "0xB07Ee28C51009e43592881e240AEd864C3a7e149"


def describe_allowlist_adapter() -> None:
    def it_validate_allowlist_endpoint() -> None:
        with pytest.raises(ValueError):
            adapter.AllowListAdapter(allowlist_endpoint="")

    def when_the_address_is_valid() -> None:
        async def it_returns_true(valid_address: str) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/valid_address.yml",
                match_on=_VCR_MATCH_ON,
            ):
                result = await adapter.AllowListAdapter().fetch(valid_address, "goerli")
                assert result == adapter.AllowListSignal(on_allowlist=True)

    def when_the_address_is_invalid() -> None:
        async def it_returns_false(invalid_address: str) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/invalid_address.yml",
                match_on=_VCR_MATCH_ON,
            ):
                result = await adapter.AllowListAdapter().fetch(
                    invalid_address, "goerli"
                )
                assert result == adapter.AllowListSignal(on_allowlist=False)

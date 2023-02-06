import pytest

from huma_signals.adapters.allowlist import adapter


@pytest.fixture
def valid_address() -> str:
    return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0"


@pytest.fixture
def invalid_address() -> str:
    return "0xB07Ee28C51009e43592881e240AEd864C3a7e149"


def describe_allowlist_adapter() -> None:
    async def it_works_e2e(valid_address: str, invalid_address: str) -> None:
        result = await adapter.AllowListAdapter().fetch(valid_address, "goerli")
        assert result == adapter.AllowListSignal(on_allowlist=True)

        result = await adapter.AllowListAdapter().fetch(invalid_address, "goerli")
        assert result == adapter.AllowListSignal(on_allowlist=False)

    def it_validate_allowlist_endpoint() -> None:
        with pytest.raises(ValueError):
            adapter.AllowListAdapter(allowlist_endpoint="")

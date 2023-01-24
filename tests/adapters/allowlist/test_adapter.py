import pytest

from huma_signals.adapters.allowlist import adapter


@pytest.fixture(scope="session", autouse=True)
def valid_address() -> str:
    return "0x41D33Eb68af3efa12d69B68FFCaF1887F9eCfEC0"


@pytest.fixture(scope="session", autouse=True)
def invalid_address() -> str:
    return "0xB07Ee28C51009e43592881e240AEd864C3a7e149"


def describe_allowlist_adapter() -> None:
    def it_works_e2e(valid_address: str, invalid_address: str) -> None:
        result = adapter.AllowListAdapter.fetch(valid_address, "goerli")
        assert result == adapter.AllowListSignal(on_allowlist=True)

        result = adapter.AllowListAdapter.fetch(invalid_address, "goerli")
        assert result == adapter.AllowListSignal(on_allowlist=False)

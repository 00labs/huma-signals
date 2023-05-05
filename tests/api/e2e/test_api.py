import pytest

from huma_signals.api import models
from tests.helpers import api_helpers, vcr_helpers

_FIXTURE_BASE_PATH = "/api/e2e/api"


def describe_fetch() -> None:
    @pytest.fixture
    def borrower_wallet_address() -> str:
        return "0xc38B0528097B8076048BEdf4330644F068CEC2e6"

    @pytest.fixture
    def signal_request(borrower_wallet_address: str) -> models.SignalFetchRequest:
        return models.SignalFetchRequest(
            signal_names=[
                "request_network.payer_tenure",
                "request_network.payer_recent",
                "request_network.payee_tenure",
                "request_network.payee_recent",
                "request_network.mutual_count",
                "request_network.payee_match_borrower",
                "request_network.borrower_own_invoice",
            ],
            adapter_inputs={
                "borrower_wallet_address": borrower_wallet_address,
                "receivable_param": "0xd4d3",
            },
        )

    async def it_fetches_the_signals(signal_request: models.SignalFetchRequest) -> None:
        with vcr_helpers.use_cassette(
            fixture_file_path=f"{_FIXTURE_BASE_PATH}/fetch.yml"
        ):
            resp = await api_helpers.post_request(
                "/fetch",
                data=signal_request.json(),
            )
            assert resp.status_code == 200

        signals = resp.json()["signals"]
        assert set(signals.keys()) == set(signal_request.signal_names)
        assert signals["request_network.payee_tenure"] > 570
        assert signals["request_network.payee_match_borrower"]
        assert signals["request_network.borrower_own_invoice"]

    def with_invalid_borrower_address() -> None:
        @pytest.fixture
        def borrower_wallet_address() -> str:
            return "0xabc"

        async def it_returns_400(signal_request: models.SignalFetchRequest) -> None:
            resp = await api_helpers.post_request(
                "/fetch",
                data=signal_request.json(),
            )
            assert resp.status_code == 400

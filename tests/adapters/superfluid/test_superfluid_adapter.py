import pytest

from huma_signals import exceptions
from huma_signals.adapters.superfluid import superfluid_adapter
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/adapters/superfluid"


def describe_SuperfluidAdapter() -> None:
    @pytest.fixture
    def borrower_wallet_address() -> str:
        return "0xF6c0ACD62e69669155f314D6A6E22f5cF63fab4E"

    @pytest.fixture
    def payer_wallet_address() -> str:
        return "0x60758B3A6933192D0Ac28Fc1f675364bb4dFAb1d"

    @pytest.fixture
    def super_token_address() -> str:
        return "0x42bb40bF79730451B11f6De1CbA222F17b87Afd7"

    def describe_fetch() -> None:
        async def it_fetches_the_signals(
            borrower_wallet_address: str,
            payer_wallet_address: str,
            super_token_address: str,
        ) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/fetch.yml",
                match_on=["alchemy_url"],
            ):
                signals = await superfluid_adapter.SuperfluidAdapter().fetch(
                    borrower_wallet_address=borrower_wallet_address,
                    payer_wallet_address=payer_wallet_address,
                    super_token_address=super_token_address,
                )
                assert signals.current_flow_rate == 999975694444444443

        def if_the_stream_cannot_be_found() -> None:
            @pytest.fixture
            def borrower_wallet_address() -> str:
                return "0x808E2154028cA8623E2704119df0aE8e39D87a8E"

            async def it_raises_exception(
                borrower_wallet_address: str,
                payer_wallet_address: str,
                super_token_address: str,
            ) -> None:
                with pytest.raises(exceptions.SuperfluidStreamNotFoundException):
                    with vcr_helpers.use_cassette(
                        fixture_file_path=f"{_FIXTURE_BASE_PATH}/fetch_stream_not_found.yml",
                        match_on=["alchemy_url"],
                    ):
                        await superfluid_adapter.SuperfluidAdapter().fetch(
                            borrower_wallet_address=borrower_wallet_address,
                            payer_wallet_address=payer_wallet_address,
                            super_token_address=super_token_address,
                        )

        def if_some_address_is_invalid() -> None:
            @pytest.fixture
            def borrower_wallet_address() -> str:
                return "0xabc"

            async def it_raises_exception(
                borrower_wallet_address: str,
                payer_wallet_address: str,
                super_token_address: str,
            ) -> None:
                with pytest.raises(exceptions.InvalidAddressException):
                    await superfluid_adapter.SuperfluidAdapter().fetch(
                        borrower_wallet_address=borrower_wallet_address,
                        payer_wallet_address=payer_wallet_address,
                        super_token_address=super_token_address,
                    )

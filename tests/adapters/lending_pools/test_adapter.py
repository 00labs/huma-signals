from unittest import mock

import pytest
import pytest_mock
from huma_utils import web3_utils
from web3 import exceptions as web3_exceptions

from huma_signals import exceptions
from huma_signals.adapters.lending_pools import adapter
from tests.helpers import address_helpers, vcr_helpers

_FIXTURE_BASE_PATH = "/adapters/lending_pools"


def describe_LendingPoolAdapter() -> None:
    @pytest.fixture
    def pool_address() -> str:
        return "0xA22D20FB0c9980fb96A9B0B5679C061aeAf5dDE4"

    def describe_fetch() -> None:
        async def it_fetches_the_signals(pool_address: str) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/credit_line_pool_signals.yml",
                match_on=["alchemy_url"],
            ):
                signals = await adapter.LendingPoolAdapter().fetch(pool_address)
                assert signals.pool_address == pool_address
                assert signals.apr == 1000
                assert signals.max_credit_amount == 10_000_000_000
                assert signals.token_address == "0xf17FF940864351631b1be3ac03702dEA085ba51c"
                assert signals.token_name == "TestToken"
                assert signals.token_symbol == "USDC"
                assert signals.token_decimal == 6
                assert signals.nft_contract_address == "0x026D2AED6f1E9Db160b79688Ea0CE1ABaee4Dc39"
                assert signals.interval_in_days_max == 90
                assert signals.interval_in_days_min == 0
                assert signals.invoice_amount_ratio == 0.8
                assert signals.is_testnet is True

        def with_invoice_factoring_pool() -> None:
            @pytest.fixture
            def pool_address() -> str:
                return "0x11672c0bBFF498c72BC2200f42461c0414855042"

            async def it_fetches_the_signals(pool_address: str) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/invoice_factoring_pool_signals.yml",
                    match_on=["alchemy_url"],
                ):
                    signals = await adapter.LendingPoolAdapter().fetch(pool_address)
                    assert signals.pool_address == pool_address
                    assert signals.apr == 0
                    assert signals.max_credit_amount == 1_000_000_000
                    assert signals.token_address == "0xf17FF940864351631b1be3ac03702dEA085ba51c"
                    assert signals.token_name == "TestToken"
                    assert signals.token_symbol == "USDC"
                    assert signals.token_decimal == 6
                    assert signals.nft_contract_address == "0x026D2AED6f1E9Db160b79688Ea0CE1ABaee4Dc39"
                    assert signals.interval_in_days_max == 90
                    assert signals.interval_in_days_min == 0
                    assert signals.invoice_amount_ratio == 0.8
                    assert signals.is_testnet is True

            def with_invalid_pool_address() -> None:
                @pytest.fixture
                def pool_address() -> str:
                    return address_helpers.fake_hex_address()

                async def it_throws_error(pool_address: str) -> None:
                    with pytest.raises(exceptions.PoolSettingsNotFoundException):
                        await adapter.LendingPoolAdapter().fetch(pool_address)

            def when_contract_call_fails() -> None:
                # Usually we should refrain from mocking since it's testing implementation details
                # of a function instead of its behaviors. But since it's hard to trigger an exception
                # on purpose for contract calls, let's use mocking here, but know that it's not the
                # recommended practice.
                @pytest.fixture
                def mock_pool_contract(
                    mocker: pytest_mock.MockerFixture,
                ) -> mock.MagicMock:
                    mock_pool_contract = mocker.MagicMock()
                    mock_pool_contract.functions.poolConfig.return_value.call.side_effect = (
                        web3_exceptions.Web3Exception()
                    )
                    return mock_pool_contract

                @pytest.fixture
                def mock_w3(mocker: pytest_mock.MockerFixture) -> mock.MagicMock:
                    mock_w3 = mocker.MagicMock()
                    mocker.patch.object(web3_utils, "get_w3", return_value=mock_w3)
                    return mock_w3

                def when_pool_config_call_fails() -> None:
                    async def it_throws_error(
                        mock_w3: mock.MagicMock,
                        mock_pool_contract: mock.MagicMock,
                        pool_address: str,
                    ) -> None:
                        mock_w3.eth.contract.return_value = mock_pool_contract

                        with pytest.raises(exceptions.ContractCallFailedException):
                            await adapter.LendingPoolAdapter().fetch(pool_address)

                def when_pool_summary_call_fails() -> None:
                    async def it_throws_error(
                        mocker: pytest_mock.MockerFixture,
                        mock_w3: mock.MagicMock,
                        mock_pool_contract: mock.MagicMock,
                        pool_address: str,
                    ) -> None:
                        mock_pool_config_contract = mocker.MagicMock()
                        mock_pool_config_contract.functions.getPoolSummary.return_value.call.side_effect = (
                            web3_exceptions.Web3Exception()
                        )
                        mock_w3.eth.contract.side_effect = [
                            mock_pool_contract,
                            mock_pool_config_contract,
                        ]

                        with pytest.raises(exceptions.ContractCallFailedException):
                            await adapter.LendingPoolAdapter().fetch(pool_address)

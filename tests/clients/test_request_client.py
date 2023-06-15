import datetime
import decimal

import pandas as pd
import pydantic
import pytest
import web3
from huma_utils import chain_utils

from huma_signals.clients.request_client import request_client
from tests.fixtures.clients.request import request_type_factories
from tests.helpers import vcr_helpers

_FIXTURE_BASE_PATH = "/clients/request_client"


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    request_network_invoice_api_url: str


settings = Settings()


def describe_RequestClient() -> None:
    @pytest.fixture
    def client(rn_subgraph_endpoint_url: str) -> request_client.RequestClient:
        return request_client.RequestClient(
            request_network_subgraph_endpoint_url=rn_subgraph_endpoint_url,
            invoice_api_url=settings.request_network_invoice_api_url,
        )

    def describe_get_payments() -> None:
        def when_to_address_is_none() -> None:
            async def it_returns_payment_history(
                client: request_client.RequestClient, from_address: str
            ) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_payments_no_to_address.yml"
                ):
                    payments = await client.get_payments(
                        from_address,
                        None,
                    )
                    assert len(payments) > 0
                    assert payments[-1]["from"] == from_address
                    assert payments[-1]["to"].startswith("0x")

        def when_from_address_is_none() -> None:
            async def it_returns_payment_history(
                client: request_client.RequestClient, from_address: str, to_address: str
            ) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_payments_no_from_address.yml"
                ):
                    payments = await client.get_payments(
                        None,
                        to_address,
                    )
                    assert len(payments) > 0
                    assert payments[-1]["to"] == to_address
                    assert payments[-1]["from"].startswith("0x")

        def when_both_addresses_are_present() -> None:
            async def it_returns_payment_history(
                client: request_client.RequestClient, from_address: str, to_address: str
            ) -> None:
                with vcr_helpers.use_cassette(
                    fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_payments.yml"
                ):
                    payments = await client.get_payments(
                        from_address,
                        to_address,
                    )
                    assert len(payments) > 0
                    assert payments[-1]["to"] == to_address
                    assert payments[-1]["from"] == from_address

    def describe_get_invoice() -> None:
        @pytest.fixture
        def request_id() -> str:
            return "016fed96cde5f301cb7340ff88c1ba5da96d48485d39f6a146f7bf7794433d3959"

        @pytest.fixture
        def payer_wallet_address() -> str:
            return "0x8b99407A4395714B706415277f17b4d549608AFe"

        @pytest.fixture
        def payee_wallet_address() -> str:
            return "0xc38B0528097B8076048BEdf4330644F068CEC2e6"

        async def it_returns_the_invoice(
            client: request_client.RequestClient,
            request_id: str,
            payer_wallet_address: str,
            payee_wallet_address: str,
        ) -> None:
            with vcr_helpers.use_cassette(
                fixture_file_path=f"{_FIXTURE_BASE_PATH}/get_invoice.yml"
            ):
                invoice = await client.get_invoice(request_id=request_id)
                assert (
                    web3.Web3.to_checksum_address(invoice.payer) == payer_wallet_address
                )
                assert invoice.currency == "USDC"
                assert invoice.amount == decimal.Decimal("100_000_000")
                assert (
                    web3.Web3.to_checksum_address(invoice.payee) == payee_wallet_address
                )
                assert invoice.creation_date == datetime.datetime(
                    2023, 4, 17, 0, 36, 46
                )
                assert invoice.token_id == "0xd4d3"

    def describe_enrich_payments_data() -> None:
        @pytest.fixture
        def chain() -> chain_utils.Chain:
            return chain_utils.Chain.ETHEREUM

        @pytest.fixture
        def token_address() -> str:
            # USDC.
            return "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"

        @pytest.fixture
        def payments_data(token_address: str) -> pd.DataFrame:
            raw_data = request_type_factories.PaymentFactory.create_batch(
                size=10, token_address=token_address
            )
            return pd.DataFrame.from_records(raw_data)

        def it_enriches_the_payment_data(
            payments_data: pd.DataFrame, chain: chain_utils.Chain
        ) -> None:
            enriched_data = request_client.RequestClient.enrich_payments_data(
                payments_data, chain=chain
            )
            assert enriched_data["token_symbol"].eq("USDC").all()
            assert enriched_data["amount"].apply(lambda v: isinstance(v, float)).all()

    def describe_get_payment_stats() -> None:
        @pytest.fixture
        def num_payments() -> int:
            return 10

        @pytest.fixture
        def enriched_payments_data(num_payments: int) -> pd.DataFrame:
            raw_data = pd.DataFrame.from_records(
                request_type_factories.PaymentFactory.create_batch(size=num_payments)
            )
            return request_client.RequestClient.enrich_payments_data(
                raw_data, chain=chain_utils.Chain.ETHEREUM
            )

        def it_summarizes_payment_stats(
            enriched_payments_data: pd.DataFrame, num_payments: int
        ) -> None:
            stats = request_client.RequestClient.get_payment_stats(
                enriched_df=enriched_payments_data
            )
            assert stats["total_txns"] == num_payments
            assert stats["unique_payees"] == num_payments
            assert stats["unique_payees"] == num_payments

import pytest
from huma_utils import chain_utils


def describe_chain() -> None:
    def describe_chain_() -> None:
        def it_has_correct_number_of_chain_utils() -> None:
            assert len(chain_utils.Chain) == 4

        def it_support_polygon() -> None:
            assert chain_utils.Chain.POLYGON == chain_utils.Chain("POLYGON")
            assert chain_utils.Chain.POLYGON.chain_name() == "polygon"
            assert chain_utils.Chain.POLYGON.is_testnet() is False

        def it_support_eth() -> None:
            assert chain_utils.Chain.ETHEREUM == chain_utils.Chain("ETHEREUM")
            assert chain_utils.Chain.ETHEREUM.chain_name() == "ethereum"
            assert chain_utils.Chain.ETHEREUM.is_testnet() is False

        def it_support_goerli() -> None:
            assert chain_utils.Chain.GOERLI == chain_utils.Chain("GOERLI")
            assert chain_utils.Chain.GOERLI.chain_name() == "goerli"
            assert chain_utils.Chain.GOERLI.is_testnet() is True

        def it_does_not_support_other_chain_utils() -> None:
            with pytest.raises(ValueError):
                assert chain_utils.Chain("SOME_CHAIN") is None

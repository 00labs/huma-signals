import pytest

from huma_signals.commons import chains


def describe_chain() -> None:
    def describe_chain_() -> None:
        def it_has_correct_number_of_chains() -> None:
            assert len(chains.Chain) == 3

        def it_support_polygon() -> None:
            assert chains.Chain.POLYGON == chains.Chain("POLYGON")
            assert chains.Chain.POLYGON.chain_name() == "polygon"
            assert chains.Chain.POLYGON.is_testnet() is False

        def it_support_eth() -> None:
            assert chains.Chain.ETHEREUM == chains.Chain("ETHEREUM")
            assert chains.Chain.ETHEREUM.chain_name() == "ethereum"
            assert chains.Chain.ETHEREUM.is_testnet() is False

        def it_support_goerli() -> None:
            assert chains.Chain.GOERLI == chains.Chain("GOERLI")
            assert chains.Chain.GOERLI.chain_name() == "goerli"
            assert chains.Chain.GOERLI.is_testnet() is True

        def it_does_not_support_other_chains() -> None:
            with pytest.raises(ValueError):
                assert chains.Chain("SOME_CHAIN") is None

        def it_can_get_chain_from_chain_name() -> None:
            assert chains.Chain.from_chain_name("polygon") == chains.Chain.POLYGON
            assert chains.Chain.from_chain_name("ethereum") == chains.Chain.ETHEREUM
            assert chains.Chain.from_chain_name("goerli") == chains.Chain.GOERLI
            assert chains.Chain.from_chain_name("matic") == chains.Chain.POLYGON
            assert chains.Chain.from_chain_name("eth") == chains.Chain.ETHEREUM
            assert chains.Chain.from_chain_name("MAINNET") == chains.Chain.ETHEREUM

            with pytest.raises(ValueError):
                assert chains.Chain.from_chain_name("SOME_CHAIN") is None

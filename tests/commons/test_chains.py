import os

import pytest

from huma_signals.commons.chains import Chain, get_w3


def describe_chain():
    def describe_chain_():
        def it_has_correct_number_of_chains():
            assert len(Chain) == 3

        def it_support_polygon():
            assert Chain.POLYGON == Chain("POLYGON")
            assert Chain.POLYGON.chain_name() == "polygon"
            assert Chain.POLYGON.is_testnet() is False

        def it_support_eth():
            assert Chain.ETHEREUM == Chain("ETHEREUM")
            assert Chain.ETHEREUM.chain_name() == "ethereum"
            assert Chain.ETHEREUM.is_testnet() is False

        def it_support_goerli():
            assert Chain.GOERLI == Chain("GOERLI")
            assert Chain.GOERLI.chain_name() == "goerli"
            assert Chain.GOERLI.is_testnet() is True

        def it_does_not_support_other_chains():
            with pytest.raises(ValueError):
                assert Chain("SOME_CHAIN") is None


def describe_get_w3():
    def it_can_get_w3():
        alchemy_key = os.environ.get("ALCHEMY_KEY_GOERLI")
        w3 = get_w3(Chain.GOERLI, alchemy_key=alchemy_key)
        assert w3 is not None
        assert w3.isConnected() is True

        latest_block = w3.eth.getBlock("latest")
        assert latest_block is not None
        assert latest_block["number"] > 0
        assert latest_block["hash"] is not None

        block = w3.eth.getBlock(latest_block["hash"])
        assert block is not None
        assert block["number"] == latest_block["number"]

    def it_can_get_w3_from_env():
        w3 = get_w3(Chain.GOERLI)

        assert w3 is not None
        assert w3.isConnected() is True

        latest_block = w3.eth.getBlock("latest")
        assert latest_block is not None
        assert latest_block["number"] > 0
        assert latest_block["hash"] is not None

        block = w3.eth.getBlock(latest_block["hash"])
        assert block is not None
        assert block["number"] == latest_block["number"]

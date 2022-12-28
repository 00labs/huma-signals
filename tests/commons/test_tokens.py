from web3 import Web3

from huma_signals.commons.chains import Chain
from huma_signals.commons.tokens import TOKEN_ADDRESS_MAPPING, TOKEN_USD_PRICE_MAPPING


def describe_TOKEN_ADDRESS_MAPPING():
    def it_contains_supported_chains():
        assert Chain.ETHEREUM in TOKEN_ADDRESS_MAPPING
        assert Chain.POLYGON in TOKEN_ADDRESS_MAPPING
        assert Chain.GOERLI in TOKEN_ADDRESS_MAPPING

    def it_contains_supported_tokens():
        for chain in Chain:
            assert "USDC" in TOKEN_ADDRESS_MAPPING[chain].values()
            assert "USDT" in TOKEN_ADDRESS_MAPPING[chain].values()
            assert "DAI" in TOKEN_ADDRESS_MAPPING[chain].values()

    def it_has_all_token_names_in_uppercase():
        for chain in Chain:
            for token in TOKEN_ADDRESS_MAPPING[chain].values():
                assert token == token.upper()

    def it_has_all_token_address_in_lowercase():
        for chain in Chain:
            for token in TOKEN_ADDRESS_MAPPING[chain].keys():
                assert token == token.lower()

    def it_has_all_tokens_valid_eth_addresses():
        for chain in Chain:
            for token in TOKEN_ADDRESS_MAPPING[chain].keys():
                assert Web3.isAddress(token)


def describe_TOKEN_USD_PRICE_MAPPING():
    def it_contains_supported_tokens():
        assert "USDC" in TOKEN_USD_PRICE_MAPPING
        assert "USDT" in TOKEN_USD_PRICE_MAPPING
        assert "DAI" in TOKEN_USD_PRICE_MAPPING

    def it_has_all_token_names_in_uppercase():
        for token in TOKEN_USD_PRICE_MAPPING.keys():
            assert token == token.upper()

    def it_has_all_token_prices_positive():
        for token_usd_price in TOKEN_USD_PRICE_MAPPING.values():
            assert token_usd_price > 0

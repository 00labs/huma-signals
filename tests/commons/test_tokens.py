import web3

from huma_signals.commons import chains, tokens


def describe_TOKEN_ADDRESS_MAPPING() -> None:
    def it_contains_supported_chains() -> None:
        assert chains.Chain.ETHEREUM in tokens.TOKEN_ADDRESS_MAPPING
        assert chains.Chain.POLYGON in tokens.TOKEN_ADDRESS_MAPPING
        assert chains.Chain.GOERLI in tokens.TOKEN_ADDRESS_MAPPING

    def it_contains_supported_tokens() -> None:
        for chain in chains.Chain:
            assert "USDC" in tokens.TOKEN_ADDRESS_MAPPING[chain].values()
            assert "USDT" in tokens.TOKEN_ADDRESS_MAPPING[chain].values()
            assert "DAI" in tokens.TOKEN_ADDRESS_MAPPING[chain].values()

    def it_has_all_token_names_in_uppercase() -> None:
        for chain in chains.Chain:
            for token in tokens.TOKEN_ADDRESS_MAPPING[chain].values():
                assert token == token.upper()

    def it_has_all_token_address_in_lowercase() -> None:
        for chain in chains.Chain:
            for token in tokens.TOKEN_ADDRESS_MAPPING[chain]:
                assert token == token.lower()

    def it_has_all_tokens_valid_eth_addresses() -> None:
        for chain in chains.Chain:
            for token in tokens.TOKEN_ADDRESS_MAPPING[chain]:
                assert web3.Web3.is_address(token)


def describe_TOKEN_USD_PRICE_MAPPING() -> None:
    def it_contains_supported_tokens() -> None:
        assert "USDC" in tokens.TOKEN_USD_PRICE_MAPPING
        assert "USDT" in tokens.TOKEN_USD_PRICE_MAPPING
        assert "DAI" in tokens.TOKEN_USD_PRICE_MAPPING

    def it_has_all_token_names_in_uppercase() -> None:
        for token in tokens.TOKEN_USD_PRICE_MAPPING:
            assert token == token.upper()

    def it_has_all_token_prices_positive() -> None:
        for token_usd_price in tokens.TOKEN_USD_PRICE_MAPPING.values():
            assert token_usd_price > 0

from huma_signals.commons import chains

TOKEN_ADDRESS_MAPPING = {
    chains.Chain.ETHEREUM: {
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
        "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
        "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
        # "0x3845badade8e6dff049820680d1f14bd3903a5d0": "SAND",
        # "0xc944e90c64b2c07662a292be6244bdf05cda44a7": "GRT",
        # "0x967da4048cd07ab37855c090aaf366e4ce1b9f48": "OCEAN",
        # "0x8f8221afbb33998d8584a2b05749ba73c37a938a": "REQ",
    },
    chains.Chain.POLYGON: {
        "0x2791bca1f2de4661ed88a30c99a7a9449aa84174": "USDC",
        "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063": "DAI",
        "0xc2132d05d31c914a87c6611c10748aeb04b58e8f": "USDT",
    },
    chains.Chain.GOERLI: {
        "0x07865c6e87b9f70255377e024ace6630c1eaa37f": "USDC",
        "0xdc31ee1784292379fbb2964b3b9c4124d8f89c60": "DAI",
        "0x56705db9f87c8a930ec87da0d458e00a657fccb0": "USDT",
    },
}

TOKEN_USD_PRICE_MAPPING = {
    "USDC": 1.0 / 10**6,
    "DAI": 1.0 / 10**18,
    "USDT": 1.0 / 10**6,
}

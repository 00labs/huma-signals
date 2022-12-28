from huma_signals.commons.chains import Chain


def get_rn_subgraph_endpoint_url(chain_name: str) -> str:
    chain = Chain.from_chain_name(chain_name)
    if chain == Chain.ETHEREUM:
        return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-mainnet"
    elif chain == Chain.POLYGON:
        return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-matic"
    elif chain == Chain.GOERLI:
        return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-goerli"

    raise ValueError(f"Unsupported chain chain: {chain_name}")


def get_rn_invoice_api_url(chain_name: str) -> str:
    chain = Chain.from_chain_name(chain_name)
    if chain == Chain.POLYGON:
        return "https://polygon.huma.finance/invoice"
    elif chain == Chain.GOERLI:
        return "https://goerli.api.huma.finance/invoice"

    raise ValueError(f"Unsupported chain chain: {chain_name}")

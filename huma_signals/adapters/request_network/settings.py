from huma_signals.commons import chains


def get_rn_subgraph_endpoint_url(chain_name: str) -> str:
    chain = chains.Chain.from_chain_name(chain_name)
    if chain == chains.Chain.ETHEREUM:
        return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-mainnet"
    if chain == chains.Chain.POLYGON:
        return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-matic"
    if chain == chains.Chain.GOERLI:
        return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-goerli"

    raise ValueError(f"Unsupported chain chain: {chain_name}")


def get_rn_invoice_api_url(chain_name: str) -> str:
    chain = chains.Chain.from_chain_name(chain_name)
    if chain == chains.Chain.POLYGON:
        return "https://polygon.api.huma.finance/invoice"
    if chain == chains.Chain.GOERLI:
        return "https://goerli.api.huma.finance/invoice"

    raise ValueError(f"Unsupported chain chain: {chain_name}")

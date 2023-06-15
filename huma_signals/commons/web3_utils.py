from __future__ import annotations

from typing import Any, Dict, Sequence, Type, Union

import web3
from web3 import eth, geth, module, net

from huma_utils import chain_utils

_WEB3_CHAIN_NETWORK_ID: Dict[chain_utils.Chain, str] = {
    chain_utils.Chain.ETHEREUM: "1",
    chain_utils.Chain.GOERLI: "5",
    chain_utils.Chain.POLYGON: "137",
    chain_utils.Chain.MUMBAI: "80001",
}

_MODULES: Dict[str, Union[Type[module.Module], Sequence[Any]]] = {
    "eth": eth.AsyncEth,  # type: ignore[attr-defined]
    "net": net.AsyncNet,
    "geth": (
        geth.Geth,
        {
            "txpool": geth.AsyncGethTxPool,
            "personal": geth.AsyncGethPersonal,
            "admin": geth.AsyncGethAdmin,
        },
    ),
}


async def get_w3(chain: chain_utils.Chain, web3_provider_url: str) -> web3.Web3:
    w3 = web3.Web3(
        provider=web3.Web3.AsyncHTTPProvider(web3_provider_url), modules=_MODULES
    )
    if await w3.net.version != _WEB3_CHAIN_NETWORK_ID.get(chain):  # type: ignore
        raise ValueError(f"Web3 provider is not compatible with chain {chain.name}")
    return w3

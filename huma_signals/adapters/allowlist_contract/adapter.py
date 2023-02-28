import pathlib
import aiofiles

import orjson
import pydantic
import web3
from typing import Any, ClassVar, List

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.utils.etherscan_client import EtherscanClient
from huma_signals.commons import web3_utils
from huma_signals.commons.chains import Chain
from huma_signals.settings import settings


class AllowListSignal(models.HumaBaseModel):
    """
    Signals emitted by the allowlist adapter.

    Note this is a temporary adapter and will be removed once the allowlist is integrated into the EAs.
    """

    on_allowlist: bool = False

class AllowListContractAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "allowlist_contract"
    required_inputs: ClassVar[List[str]] = ["contract_address", "chain", "borrower_wallet_address"]
    signals: ClassVar[List[str]] = list(AllowListSignal.__fields__.keys())
    etherscan_client: EtherscanClient = pydantic.Field(default=EtherscanClient())


    async def fetch(  # pylint: disable=arguments-differ
        self, contract_address: str, chain: str, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> AllowListSignal:
        chain_obj = Chain.from_chain_name(chain)
        w3 = await web3_utils.get_w3(chain_obj, settings.web3_provider_url)

        abi = await self._get_abi(chain_obj)
        allow_list_contract = w3.eth.contract(
            address=web3.Web3.to_checksum_address(contract_address),
            abi=orjson.loads(abi),
        )

        whitelisted_borrowers = await allow_list_contract.functions.getWhitelistedBorrowers().call()
        return AllowListSignal(
            on_allowlist=(borrower_wallet_address in whitelisted_borrowers)
        )

    async def _get_abi(self, chain_obj):
        if chain_obj == Chain.LOCAL:
            async with aiofiles.open(pathlib.Path(__file__).parent.resolve() / "abi" / "YourContract.json",
                                     encoding="utf-8") as f:
                return await f.read()
        else:
            return await self.etherscan_client.get_contract_abi("0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")

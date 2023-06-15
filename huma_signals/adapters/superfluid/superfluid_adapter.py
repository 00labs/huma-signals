import httpx
import structlog
import web3
from huma_utils import chain_utils

from huma_signals import exceptions
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.superfluid import superfluid_models
from huma_signals.adapters.superfluid.settings import settings

logger = structlog.get_logger()


_CURRENT_STREAM_QUERY = """
query HumaCurrentStream($sender: String, $receiver: String, $token: String) {
    streams(
        where: {
            sender: $sender,
            receiver: $receiver,
            token: $token
        }
        first: 1
        orderBy: updatedAtTimestamp
        orderDirection: desc
        currentFlowRate_gt: 0
    ) {
        id
        currentFlowRate
        createdAtTimestamp
        updatedAtTimestamp
    }
}
"""


class SuperfluidAdapter(adapter_models.SignalAdapterBase):
    def __init__(
        self,
        superfluid_subgraph_endpoint_url: str = settings.superfluid_subgraph_endpoint_url,
        chain: chain_utils.Chain = settings.chain,
    ) -> None:
        self.superfluid_subgraph_endpoint_url = superfluid_subgraph_endpoint_url
        self.chain = chain

    async def fetch(  # pylint: disable=arguments-differ
        self,
        borrower_wallet_address: str,
        payer_wallet_address: str,
        super_token_address: str,
    ) -> superfluid_models.SuperfluidSignals:
        for address in [
            borrower_wallet_address,
            payer_wallet_address,
            super_token_address,
        ]:
            if not web3.Web3.is_address(address):
                raise exceptions.InvalidAddressException(f"Invalid address: {address}")

        sender_address = payer_wallet_address.lower()
        receiver_address = borrower_wallet_address.lower()
        token_address = super_token_address.lower()
        current_stream = await self._get_current_stream(
            sender_address=sender_address,
            receiver_address=receiver_address,
            token_address=token_address,
        )
        # Pylint doesn't recognize the `@combomethod` decorator that makes a method
        # callable as a class method.
        stream_id = web3.Web3.solidity_keccak(  # pylint: disable=no-value-for-parameter
            abi_types=["address", "address", "address"],
            values=[
                web3.Web3.to_checksum_address(token_address),
                web3.Web3.to_checksum_address(sender_address),
                web3.Web3.to_checksum_address(receiver_address),
            ],
        ).hex()
        return superfluid_models.SuperfluidSignals(
            current_flow_rate=current_stream.current_flow_rate,
            stream_id=stream_id,
        )

    async def _get_current_stream(
        self, sender_address: str, receiver_address: str, token_address: str
    ) -> superfluid_models.SuperfluidStream:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.superfluid_subgraph_endpoint_url,
                    json={
                        "query": _CURRENT_STREAM_QUERY,
                        "variables": {
                            "sender": sender_address,
                            "receiver": receiver_address,
                            "token": token_address,
                        },
                    },
                )
                streams = resp.json()["data"]["streams"]
                return superfluid_models.SuperfluidStream(**streams[0])
        except KeyError as e:
            message = "No data returned from query"
            logger.exception(message, resp_body=resp.json())
            raise exceptions.SuperfluidException(message=message) from e
        except IndexError as e:
            message = (
                "Stream not found for sender, receiver and token:"
                f" ({sender_address}, {receiver_address}, {token_address})"
            )
            logger.exception(message)
            raise exceptions.SuperfluidStreamNotFoundException(message=message) from e
        except Exception as e:
            message = f"Error fetching Superfluid streams: {e}"
            logger.exception(message)
            raise exceptions.SuperfluidException(message=message) from e

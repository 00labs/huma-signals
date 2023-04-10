from typing import Any

import httpx
import structlog

from huma_signals import exceptions
from huma_signals.settings import settings

logger = structlog.get_logger(__name__)

_DEFAULT_GRAPHQL_CHUNK_SIZE = 1000


class RequestClient:
    """
    Translation layer for interacting with the Request Network/Request Finance API.
    """

    def __init__(
        self,
        rn_subgraph_endpoint_url: str = settings.request_network_subgraph_endpoint_url,
    ) -> None:
        self.rn_subgraph_endpoint_url = rn_subgraph_endpoint_url

    async def get_payments(
        self,
        from_address: str | None,
        to_address: str | None,
    ) -> list[Any]:
        where_clause = ""
        if from_address:
            where_clause += f'from: "{from_address}",\n'
        if to_address:
            where_clause += f'to: "{to_address}",\n'

        payments = []
        last_chunk_size = _DEFAULT_GRAPHQL_CHUNK_SIZE
        last_id = ""
        try:
            async with httpx.AsyncClient() as client:
                while last_chunk_size == _DEFAULT_GRAPHQL_CHUNK_SIZE:
                    query = f"""
                        query HumaRequestNetworkPayments {{
                            payments(
                                first: {_DEFAULT_GRAPHQL_CHUNK_SIZE},
                                where: {{
                                    {where_clause}
                                    id_gt: "{last_id}"
                                }}
                                orderBy: id,
                                orderDirection: asc
                            ) {{
                                id
                                contractAddress
                                tokenAddress
                                to
                                from
                                timestamp
                                txHash
                                amount
                                currency
                                amountInCrypto
                            }}
                        }}
                        """
                    resp = await client.post(
                        self.rn_subgraph_endpoint_url,
                        json={"query": query},
                    )
                    new_chunk = resp.json()["data"]["payments"]
                    payments.extend(new_chunk)
                    last_chunk_size = len(new_chunk)
                    if len(payments) > 0:
                        last_id = payments[-1]["id"]
        except KeyError as e:
            message = "No data returned from query"
            logger.exception(message, resp_body=resp.json())
            raise exceptions.RequestException(message=message) from e
        except Exception as e:
            message = f"Error fetching payments: {e}"
            logger.exception(message)
            raise exceptions.RequestException(message=message) from e

        return payments

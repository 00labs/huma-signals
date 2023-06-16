import pydantic
from huma_utils import pydantic_utils


class EthTransaction(pydantic_utils.CamelCaseAliased):
    block_number: str
    time_stamp: str
    hash: str
    nonce: str
    block_hash: str
    transaction_index: str
    from_: str = pydantic.Field(alias="from")
    to: str
    value: str
    gas: str
    gas_price: str
    is_error: str
    txreceipt_status: str
    input: str
    contract_address: str
    cumulative_gas_used: str
    gas_used: str
    confirmations: str
    method_id: str
    function_name: str


class EthTransactionResponse(pydantic_utils.CamelCaseAliased):
    status: str
    message: str
    result: list[EthTransaction]

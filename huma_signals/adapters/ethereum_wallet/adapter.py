import datetime
from typing import Any, ClassVar, List

import pandas as pd
import requests

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.settings import settings

# Sign-up at https://etherscan.io/myapikey to get an API key
ETHERSCAN_BASE_URL = "api.etherscan.io"
ETHERSCAN_API_KEY = settings.etherscan_api_key


class EthereumWalletSignals(models.HumaBaseModel):
    total_transactions: int
    total_sent: int
    total_received: int
    wallet_teneur_in_days: int
    total_income_90days: float
    total_transactions_90days: int


class EthereumWalletAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "ethereum_wallet"
    required_inputs: ClassVar[List[str]] = ["borrower_wallet_address"]
    signals: ClassVar[List[str]] = list(EthereumWalletSignals.__fields__.keys())

    @classmethod
    def _node_get_transactions(cls, wallet_address: str) -> List[Any]:
        action = "txlist"
        request_url = (
            f"https://{ETHERSCAN_BASE_URL}/"
            f"api?module=account&action={action}"
            f"&address={wallet_address}"
            f"&startblock=0&endblock=99999999"
            f"&sort=asc"
            f"&apikey={ETHERSCAN_API_KEY}"
        )
        r = requests.get(
            request_url,
            timeout=10,
        )

        if r.status_code == 200 and r.json()["status"] == "1":
            return r.json()["result"]

        return []

    @classmethod
    def fetch(  # pylint: disable=arguments-differ
        cls, borrower_wallet_address: str, *args: Any, **kwargs: Any
    ) -> EthereumWalletSignals:
        raw_txns = cls._node_get_transactions(borrower_wallet_address)
        txn_df = pd.DataFrame.from_records(raw_txns)
        if len(txn_df) == 0:
            return EthereumWalletSignals(
                total_transactions=0,
                total_sent=0,
                total_received=0,
                wallet_teneur_in_days=0,
                total_income_90days=0,
                total_transactions_90days=0,
            )
        txn_df["timeStamp"] = pd.to_datetime(txn_df["timeStamp"], unit="s")
        txn_df["value"] = txn_df["value"].astype(float)
        txn_df["from"] = txn_df["from"].str.lower()
        txn_df["to"] = txn_df["to"].str.lower()
        txn_df["is_sent"] = txn_df["from"] == borrower_wallet_address.lower()
        txn_df["is_received"] = txn_df["to"] == borrower_wallet_address.lower()
        txn_df["in_90days"] = txn_df[
            "timeStamp"
        ] > datetime.datetime.now() - pd.Timedelta(days=90)
        # TODO: Limit to selected set of tokens
        txn_df["income"] = txn_df["value"] * txn_df["is_received"].astype(float)

        return EthereumWalletSignals(
            total_transactions=len(txn_df),
            total_sent=sum(txn_df["is_sent"]),
            total_received=sum(txn_df["is_received"]),
            wallet_teneur_in_days=(
                datetime.datetime.now() - txn_df["timeStamp"].min()
            ).days,
            total_income_90days=sum(txn_df["income"] * txn_df["in_90days"]),
            total_transactions_90days=sum(txn_df["in_90days"]),
        )

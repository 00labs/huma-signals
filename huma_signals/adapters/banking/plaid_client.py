import datetime
import decimal
from typing import List, Optional

import plaid
from plaid.api import plaid_api
from plaid.model import (
    accounts_balance_get_request,
    accounts_balance_get_request_options,
    item_public_token_exchange_request,
    products,
    sandbox_public_token_create_request,
    transaction,
    transactions_get_request,
)

from huma_signals.commons import async_utils, datetime_utils

PLAID_ENVS = {
    "production": plaid.Environment.Production,
    "development": plaid.Environment.Development,
    "sandbox": plaid.Environment.Sandbox,
}


class PlaidClient:
    def __init__(self, plaid_env: str, plaid_client_id: str, plaid_secret: str) -> None:
        super().__init__()
        configuration = plaid.Configuration(
            host=PLAID_ENVS[plaid_env],
            api_key={
                "clientId": plaid_client_id,
                "secret": plaid_secret,
            },
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    async def exchange_access_token(self, public_token: str) -> str:
        request = item_public_token_exchange_request.ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = await async_utils.sync_to_async(
            self.client.item_public_token_exchange, request
        )
        return response.access_token

    async def fetch_transactions(
        self, plaid_access_token: str, lookback_days: int
    ) -> List[transaction.Transaction]:
        end_date = datetime_utils.tz_aware_utc_now().date()
        start_date = end_date - datetime.timedelta(days=lookback_days)
        request = transactions_get_request.TransactionsGetRequest(
            access_token=plaid_access_token,
            start_date=start_date,
            end_date=end_date,
        )
        response = await async_utils.sync_to_async(
            self.client.transactions_get, request
        )
        transactions = response.transactions
        while len(transactions) < response.total_transactions:
            request = transactions_get_request.TransactionsGetRequest(
                access_token=plaid_access_token,
                start_date=start_date,
                end_date=end_date,
            )
            response = self.client.transactions_get(request)
            transactions.extend(response.transactions)

        return transactions

    async def fetch_bank_account_available_balance(
        self,
        plaid_access_token: str,
    ) -> Optional[decimal.Decimal]:
        # This field is only required and used for Capital One:
        # https://plaid.com/docs/api/products/balance/#accounts-balance-get-request-options-min-last-updated-datetime.
        # Plaid gets updated balance once a day, so use 24 hours + 1 hour of leeway.
        min_last_updated_datetime = (
            datetime_utils.tz_aware_utc_now() - datetime.timedelta(hours=25)
        )
        request = accounts_balance_get_request.AccountsBalanceGetRequest(
            access_token=plaid_access_token,
            options=accounts_balance_get_request_options.AccountsBalanceGetRequestOptions(
                min_last_updated_datetime=min_last_updated_datetime,
            ),
        )
        response = await async_utils.sync_to_async(
            self.client.transactions_get, request
        )
        return response.accounts[0].balances.available

    async def create_sandbox_public_token(self, institution_id: str) -> str:
        request = sandbox_public_token_create_request.SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=[products.Products("transactions")],
        )
        response = await async_utils.sync_to_async(
            self.client.sandbox_public_token_create, request
        )
        return response.public_token

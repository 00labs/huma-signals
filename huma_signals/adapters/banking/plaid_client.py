# pylint: disable=line-too-long
import datetime
import decimal
from typing import List, Optional, Tuple

import plaid
from plaid.api import plaid_api
from plaid.model import (
    accounts_balance_get_request,
    accounts_balance_get_request_options,
    country_code,
    credit_bank_income_get_request,
    credit_bank_income_summary,
    income_verification_source_type,
    item_public_token_exchange_request,
    link_token_create_request,
    link_token_create_request_user,
    products,
    sandbox_public_token_create_request,
    sandbox_public_token_create_request_income_verification_bank_income,
    sandbox_public_token_create_request_options,
    sandbox_public_token_create_request_options_income_verification,
    transaction,
    transactions_get_request,
    user_create_request,
)

from huma_signals.commons import async_utils, datetime_utils, string_utils

PLAID_ENVS = {
    "production": plaid.Environment.Production,
    "development": plaid.Environment.Development,
    "sandbox": plaid.Environment.Sandbox,
}
_INCOME_DAYS_REQUESTED = 365


class PlaidClient:
    def __init__(self, plaid_env: str, plaid_client_id: str, plaid_secret: str) -> None:
        configuration = plaid.Configuration(
            host=PLAID_ENVS[plaid_env],
            api_key={
                "clientId": plaid_client_id,
                "secret": plaid_secret,
            },
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    async def create_user_token(self, wallet_address: str) -> str:
        # Obfuscate the wallet address by hashing it.
        request = user_create_request.UserCreateRequest(
            client_user_id=string_utils.sha256_hash_hex(wallet_address)
        )
        response = await async_utils.sync_to_async(self.client.user_create, request)
        return response.user_token

    async def create_link_token(self, wallet_address: str) -> Tuple[str, str]:
        # user_token = await self.create_user_token(wallet_address=wallet_address)
        request = link_token_create_request.LinkTokenCreateRequest(
            # `balance` product is automatically included.
            products=[products.Products("transactions")],
            client_name="Huma Financials",
            country_codes=[country_code.CountryCode("US")],
            # redirect_uri="https://app.huma.finance/",
            language="en",
            webhook="http://localhost:8001",
            link_customization_name="default",
            # income_verification=link_token_create_request_income_verification.LinkTokenCreateRequestIncomeVerification(
            #     income_source_types=[
            #         income_verification_source_type.IncomeVerificationSourceType(
            #             "BANK"
            #         )
            #     ],
            #     bank_income=link_token_create_request_income_verification_bank_income.LinkTokenCreateRequestIncomeVerificationBankIncome(  # noqa: E501
            #         days_requested=_INCOME_DAYS_REQUESTED,
            #     ),
            # ),
            user=link_token_create_request_user.LinkTokenCreateRequestUser(
                client_user_id=string_utils.sha256_hash_hex(wallet_address)
            ),
            # user_token=user_token,
        )
        response = await async_utils.sync_to_async(
            self.client.link_token_create, request
        )
        return response.link_token, ""

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

    async def fetch_bank_income(
        self, user_token: str
    ) -> credit_bank_income_summary.CreditBankIncomeSummary:
        request = credit_bank_income_get_request.CreditBankIncomeGetRequest(
            user_token=user_token,
        )
        response = self.client.credit_bank_income_get(request)
        return response.bank_income.bank_income_summary

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
            self.client.accounts_balance_get, request
        )
        return response.accounts[0].balances.available

    async def create_sandbox_public_token(
        self, institution_id: str, user_token: str
    ) -> str:
        request = sandbox_public_token_create_request.SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=[products.Products("INCOME_VERIFICATION")],
            options=sandbox_public_token_create_request_options.SandboxPublicTokenCreateRequestOptions(
                income_verification=sandbox_public_token_create_request_options_income_verification.SandboxPublicTokenCreateRequestOptionsIncomeVerification(  # noqa: E501
                    income_source_types=[
                        income_verification_source_type.IncomeVerificationSourceType(
                            "BANK"
                        )
                    ],
                    bank_income=sandbox_public_token_create_request_income_verification_bank_income.SandboxPublicTokenCreateRequestIncomeVerificationBankIncome(  # noqa: E501
                        days_requested=_INCOME_DAYS_REQUESTED,
                    ),
                ),
            ),
            user_token=user_token,
        )
        response = await async_utils.sync_to_async(
            self.client.sandbox_public_token_create, request
        )
        return response.public_token

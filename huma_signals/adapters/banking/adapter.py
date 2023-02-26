import collections
import decimal
from typing import Any, ClassVar, DefaultDict, List

import pydantic
from plaid.model import transaction

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.banking import plaid_client
from huma_signals.commons import number_utils
from huma_signals.settings import settings

_TWENTY_FOUR_MONTHS_IN_DAYS = 24 * 365
_PAYROLL_CATEGORY_ID = "21009000"


class MonthlyIncome(models.HumaBaseModel):
    # Format: YYYY-MM
    month: str
    amount: decimal.Decimal


class IncomeSignal(models.HumaBaseModel):
    monthly_income: List[MonthlyIncome]
    total_income: decimal.Decimal
    average_monthly_income: decimal.Decimal


class BankingSignal(models.HumaBaseModel):
    """
    Signals emitted by the banking adapter.
    """

    income: IncomeSignal
    current_account_balance: decimal.Decimal


class BankingAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "banking"
    required_inputs: ClassVar[List[str]] = [
        "plaid_bank_account_id",
        "plaid_public_token",
    ]
    signals: ClassVar[List[str]] = list(BankingSignal.__fields__.keys())

    plaid_env: str = pydantic.Field(default=settings.plaid_env)
    plaid_client_id: str = pydantic.Field(default=settings.plaid_client_id)
    plaid_secret: str = pydantic.Field(default=settings.plaid_secret)
    plaid_client_: plaid_client.PlaidClient = plaid_client.PlaidClient(
        plaid_env=plaid_env,
        plaid_client_id=plaid_client_id,
        plaid_secret=plaid_secret,
    )

    async def fetch(  # pylint: disable=arguments-differ
        self,
        plaid_public_token: str,
        *args: Any,
        **kwargs: Any,
    ) -> BankingSignal:
        plaid_access_token = await self.plaid_client_.exchange_access_token(
            public_token=plaid_public_token
        )
        transactions = await self.plaid_client_.fetch_transactions(
            plaid_access_token=plaid_access_token,
            lookback_days=_TWENTY_FOUR_MONTHS_IN_DAYS,
        )
        current_balance = await self.plaid_client_.fetch_bank_account_available_balance(
            plaid_access_token=plaid_access_token
        )
        return BankingSignal(
            income=self._aggregate_income_signal(transactions=transactions),
            current_account_balance=current_balance,
        )

    def _aggregate_income_signal(
        self, transactions: List[transaction.Transaction]
    ) -> IncomeSignal:
        income_by_month: DefaultDict[str, decimal.Decimal] = collections.defaultdict(
            decimal.Decimal
        )
        for tx in transactions:
            if tx.category_id == _PAYROLL_CATEGORY_ID:
                tx_month = tx.date.strftime("%Y-%m")
                # Negative amounts represent money coming into the account, so negate them.
                income_by_month[tx_month] -= decimal.Decimal(tx.amount)

        monthly_income = [
            MonthlyIncome(month=k, amount=v) for k, v in income_by_month.items()
        ]
        total_income = sum(income_by_month.values())
        average_monthly_income = number_utils.round_to_cents(
            total_income / len(monthly_income)
        )
        return IncomeSignal(
            monthly_income=monthly_income,
            total_income=total_income,
            average_monthly_income=average_monthly_income,
        )

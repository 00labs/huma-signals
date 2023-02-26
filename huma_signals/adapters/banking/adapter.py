import decimal
from typing import Any, ClassVar, List

import pydantic
from plaid.model import credit_bank_income_summary

from huma_signals import models
from huma_signals.adapters import models as adapter_models
from huma_signals.adapters.banking import plaid_client
from huma_signals.commons import datetime_utils, pydantic_utils
from huma_signals.settings import settings


class MonthlyIncome(models.HumaBaseModel):
    # Format: YYYY-MM
    month: str
    amount: decimal.Decimal

    _validate_amount = pydantic.validator("amount", allow_reuse=True, pre=True)(
        pydantic_utils.validate_amount
    )


class IncomeSignal(models.HumaBaseModel):
    monthly_income: List[MonthlyIncome]
    total_income: decimal.Decimal
    average_monthly_income: decimal.Decimal

    _validate_total_income = pydantic.validator(
        "total_income", allow_reuse=True, pre=True
    )(pydantic_utils.validate_amount)
    _validate_average_monthly_income = pydantic.validator(
        "average_monthly_income", allow_reuse=True, pre=True
    )(pydantic_utils.validate_amount)


class BankingSignal(models.HumaBaseModel):
    """
    Signals emitted by the banking adapter.
    """

    income: IncomeSignal
    current_account_balance: decimal.Decimal


class BankingAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "banking"
    required_inputs: ClassVar[List[str]] = [
        "wallet_address",
        "plaid_public_token",
    ]
    signals: ClassVar[List[str]] = list(BankingSignal.__fields__.keys())

    def __init__(
        self,
        plaid_env: str = settings.plaid_env,
        plaid_client_id: str = settings.plaid_client_id,
        plaid_secret: str = settings.plaid_secret,
    ) -> None:
        self.plaid_client = plaid_client.PlaidClient(
            plaid_env=plaid_env,
            plaid_client_id=plaid_client_id,
            plaid_secret=plaid_secret,
        )

    async def fetch(  # pylint: disable=arguments-differ
        self,
        wallet_address: str,
        plaid_public_token: str,
        *args: Any,
        **kwargs: Any,
    ) -> BankingSignal:
        user_token = await self.plaid_client.create_user_token(
            wallet_address=wallet_address
        )
        plaid_access_token = await self.plaid_client.exchange_access_token(
            public_token=plaid_public_token,
        )
        bank_income = await self.plaid_client.fetch_bank_income(user_token=user_token)
        current_balance = await self.plaid_client.fetch_bank_account_available_balance(
            plaid_access_token=plaid_access_token
        )
        return BankingSignal(
            income=self._aggregate_income_signal(bank_income=bank_income),
            current_account_balance=current_balance,
        )

    def _aggregate_income_signal(
        self, bank_income: credit_bank_income_summary.CreditBankIncomeSummary
    ) -> IncomeSignal:
        monthly_income = [
            MonthlyIncome(
                month=datetime_utils.date_to_month_str(history.start_date),
                amount=history.total_amounts.mount,
            )
            for history in bank_income.historical_summary
        ]
        total_income = bank_income.total_amounts.amount
        average_monthly_income = total_income / len(monthly_income)
        return IncomeSignal(
            monthly_income=monthly_income,
            total_income=total_income,
            average_monthly_income=average_monthly_income,
        )

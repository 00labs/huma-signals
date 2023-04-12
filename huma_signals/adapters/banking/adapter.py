import collections
import decimal
from typing import Any, ClassVar, DefaultDict, List

import pydantic
import tenacity
from plaid.model import credit_bank_income_summary, transaction

from huma_signals import constants, models
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


class MonthlyExpense(models.HumaBaseModel):
    month: str
    amount: decimal.Decimal

    _validate_amount = pydantic.validator("amount", allow_reuse=True, pre=True)(
        pydantic_utils.validate_amount
    )


class IncomeSignal(models.HumaBaseModel):
    monthly_income: List[MonthlyIncome]
    total_income: decimal.Decimal
    average_monthly_income: decimal.Decimal
    monthly_expense: List[MonthlyExpense]
    total_expense: decimal.Decimal
    average_monthly_expense: decimal.Decimal

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

    monthly_income: List[MonthlyIncome]
    total_income: decimal.Decimal
    average_monthly_income: decimal.Decimal
    monthly_expense: List[MonthlyExpense]
    total_expense: decimal.Decimal
    average_monthly_expense: decimal.Decimal
    current_account_balance: decimal.Decimal


class BankingAdapter(adapter_models.SignalAdapterBase):
    name: ClassVar[str] = "banking"
    required_inputs: ClassVar[List[str]] = [
        "plaid_public_token",
        "user_token",
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
        plaid_public_token: str,
        user_token: str,  # pylint: disable=unused-argument
        *args: Any,
        **kwargs: Any,
    ) -> BankingSignal:
        plaid_access_token = await self.plaid_client.exchange_access_token(
            public_token=plaid_public_token,
        )
        async for attempt in tenacity.AsyncRetrying(
            stop=tenacity.stop_after_attempt(3)
        ):
            with attempt:
                # Sometimes Plaid throws `PRODUCT_NOT_READY` error because the access token had
                # just been created and the requested products haven't been initialized yet. Retry
                # when this happens.
                transactions = await self.plaid_client.fetch_transactions(
                    plaid_access_token=plaid_access_token, lookback_days=365
                )

        bank_income = self._aggregate_income_and_expense_from_transactions(transactions)
        # bank_income = await self.plaid_client.fetch_bank_income(user_token=user_token)
        current_balance = await self.plaid_client.fetch_bank_account_available_balance(
            plaid_access_token=plaid_access_token
        )
        # return BankingSignal(
        #     income=self._aggregate_income_signal(bank_income=bank_income),
        #     current_account_balance=1000,
        # )
        return BankingSignal(
            monthly_income=bank_income.monthly_income,
            total_income=bank_income.total_income,
            average_monthly_income=bank_income.average_monthly_income,
            monthly_expense=bank_income.monthly_expense,
            total_expense=bank_income.total_expense,
            average_monthly_expense=bank_income.average_monthly_expense,
            current_account_balance=current_balance,
        )

    @classmethod
    def user_input_types(cls) -> List[constants.UserInputType]:
        return ["plaid-bank-link"]

    @classmethod
    def _aggregate_income_signal(
        cls, bank_income: credit_bank_income_summary.CreditBankIncomeSummary
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

    @classmethod
    def _aggregate_income_and_expense_from_transactions(
        cls,
        transactions: List[transaction.Transaction],
    ) -> IncomeSignal:
        income_by_month: DefaultDict[str, decimal.Decimal] = collections.defaultdict(
            decimal.Decimal
        )
        expense_by_month: DefaultDict[str, decimal.Decimal] = collections.defaultdict(
            decimal.Decimal
        )
        for tx in transactions:
            # if tx.category_id == 21009000:
            tx_month = tx.date.strftime("%Y-%m")
            if tx.amount <= 0:
                # Negative amounts represent money coming into the account, so negate them.
                income_by_month[tx_month] -= decimal.Decimal(tx.amount)
            else:
                expense_by_month[tx_month] += decimal.Decimal(tx.amount)

        monthly_income = [
            MonthlyIncome(month=k, amount=v) for k, v in income_by_month.items()
        ]
        total_income = sum(income_by_month.values())
        average_monthly_income = (
            total_income / len(monthly_income) if len(monthly_income) != 0 else 0
        )
        monthly_expense = [
            MonthlyExpense(month=k, amount=v) for k, v in expense_by_month.items()
        ]
        total_expense = sum(expense_by_month.values())
        average_monthly_expense = (
            total_income / len(monthly_expense) if len(monthly_expense) != 0 else 0
        )
        return IncomeSignal(
            monthly_income=monthly_income,
            total_income=total_income,
            average_monthly_income=average_monthly_income,
            monthly_expense=monthly_expense,
            total_expense=total_expense,
            average_monthly_expense=average_monthly_expense,
        )

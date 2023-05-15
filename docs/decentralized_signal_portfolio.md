# Decentralized Signal Portfolio

The Decentralized Signal Portfolio (DSP) is an open-source package that enables access to high-quality signals about a borrower's income, assets, and liabilities. These signals are collected through Signal Adapters in the package, which gather data from a variety of on-chain and off-chain sources. Any developer can contribute to the platform by adding a new Signal Adapter for a specific data source. By adding and improving these signals, we can not only improve the quality of evaluations made by Evaluation Agents but also provide a valuable data source for reuse by the broader ecosystem.

## Types of signals

In general, there are a few different flavors of signals:

- Income signals represent the amount, frequency, and other quantitative features that describe the income associated with a wallet. Predicted future income could be included as well.
- Asset signals represent the quality and quantity of the borrowers' assets.
- Liability signals represent borrowers' payment obligations from their assets and future income.

There is a wide range of sources that a Signal Adapter can be developed to fetch from. Examples include:

- On-chain sources
  - Direct payments from treasuries, i.e., Gnosis SAFE, Circle Business Account
  - Payments/invoices like Request Network, Utopia Labs, Coinshift, Superfluid
  - Positions in lending pools
  - Yield farming
  - Staking, mining, and validation income
  - Gaming income
  - NFT royalties
  - …
- Off-chain
  - Balances, transactions, and revenue like Plaid, Teller, Stripe, Quickbooks, Recurly
  - Invoices like Bill, Stripe, PayPal, Invoice2Go, Square, Zoho
  - Income data aggregates like Pinwheel, Finicity, Argyle
  - Sales data like Shopify, Amazon
  - Credit/debt data aggregates like Experian API
  - …

## Example of a Signal Adapter

See the [Ethereum Wallet Adapter](../huma_signals/adapters/ethereum_wallet) for a working example.

## Contributing new Signal Adapter

All signal adapters' code can be located under the [`huma_signals` directory](../huma_signals/).

### Adding signal definition

Add a new signal definition class to list all the signals supported by the new adapter like the one below:

```python
from huma_signals import models

class EthereumWalletSignals(models.HumaBaseModel):
    total_transactions: int
    total_sent: int
    total_received: int
    wallet_tenure_in_days: int
    total_income_90days: float
    total_transactions_90days: int
```

### Adding adapter-specific env settings

It's likely that your new Signal Adapter needs some specific env settings to run, e.g. Alchemy API key. You can create a `pydantic.Setting` class to capture all the env settings for your adapter. For example:

```python
import pydantic

class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    etherscan_base_url: str
    etherscan_api_key: str


settings = Settings()
```

Then in your adapter, you can access the env vars by referencing the settings defined above.

### Adding Signal Adapter logic

Add an Adapter class with code to fetch data from external sources and compute derived signals. Below is an example:

```python
from typing import Any

from huma_signals.adapters import models as adapter_models


class EthereumWalletAdapter(adapter_models.SignalAdapterBase):
  def __init__(self, *args: Any, **kwargs: Any):
    pass

  async def fetch(
          self, input_a: str, input_b: str, input_c: str
  ) -> EthereumWalletSignals:
    """
    The unified interface to receive inputs and return computed signals.
    """
    pass
```

### Testing

Please include extensive tests under [tests](../tests). Below are the things to keep in mind:

- Use `pytest` for test framework.
- Use `pytest-describe` to organize tests.
- If your adapter makes network requests, please use VCR cassettes to capture them so that the unit test environment do not make real network requests at runtime.
- If your tests require environment variables to run, please specify them in `pydantic.Setting` classes in your test files.

## Lifecycle of a new Signal Adapter

1. Implement the Signal Adapter according to the provided interface, and submit a pull request for review by Huma DAO.
2. If your Signal Adapter is accepted, it will be published as part of the package with the appropriate open-source license.
3. Evaluation Agents (EAs) can install the `huma-signals` package and use your Signal Adapter to fetch signals.
4. Performance and usage statistics for Signal Adapters will be regularly collected and shared as metadata. This information will be valuable to EA developers in choosing the most robust Signal Adapters, and will also be used to calculate rewards for contributors.
5. Each Signal Adapter must be maintained by its original developer, Huma DAO, or the community. The maintainer will receive rewards but is also responsible for meeting service level agreements, implementing new features, and addressing bug fixes for the Signal Adapter.

## (Coming soon) Developer participation and rewards

We invite developers to contribute to the initial development and ongoing maintenance of Signal Adapters on the DSP platform. As a way to kickstart development, Huma offers bounty programs and a portion of the protocol revenue will be allocated to reward Signal Adapter developers and maintainers. The Huma DAO will review all contributions and determine how to distribute the reward pool among different contributors. Join us and be a part of building the future of decentralized finance!

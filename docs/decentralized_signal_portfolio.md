# Decentralized Signal Portfolio

The Decentralized Signal Portfolio (DSP) is an open platform that enables access to high-quality signals about a borrower's income, assets, and liabilities. These signals are collected through Signal Adapters hosted on the DSP, which gather data from a variety of on-chain and off-chain sources. Any developer can contribute to the platform by adding a new Signal Adapter for a specific data source. By adding and improving these signals, we can not only improve the quality of evaluations made by Evaluation Agents but also provide a valuable data source for reuse by the broader ecosystem.

## Types of signals

Income-related signals help understand the amount, frequency, and other objective quantities that describe the income associated with a wallet. This can include information about predicted future income from that source as well.

Asset-related signals help understand the quality and quantity of the borrower's assets.

Liabilities are signals about borrowers' payment obligations from their assets and future income.

There is a wide range of sources that a Signal Adapter can be developed. Examples include;

- On-chain sources
  - Direct payments from treasuries, i.e., Gnosis SAFE’s, Circle Business Account
  - Payments/invoices like Request Network, Utopia Labs, Coinshift, Superfluid
  - Positions in lending pools
  - Yield farming
  - Staking, miner, and validator income
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

See the [Eth Transactions Adapter](../examples/signal_adapaters/simple_eth_transactions.py) for a working example.

## Contributing new Signal Adapter

All signal adapter codes are under the [example folder](../examples/signal_adapaters/).

### Adding signal definition

Add a new signal definition class to list all the signals supported by the new adapter.

```python
class WalletEthTransactionsSignals(Model):
    total_transactions: int
    total_sent: int
    total_received: int
    wallet_tenure_in_days: int
    total_income_90days: float
    total_transactions_90days: int
```

### Adding signal adapter logic

Add an Adapter class with code to actually fetch data from external sources and compute any derived signals:

An example:

```python
class WalletEthTransactionsAdapter(AdapterBase):
    name: ClassVar[str] = "wallet_eth_txns"
    required_inputs: ClassVar[List[str]] = ["wallet_address", "network"]
    signals: ClassVar[List[str]] = WalletEthTransactionsSignals.__fields__.keys()

    def fetch(
        self, input_a: str, input_b: str, input_c: str
    ) -> WalletEthTransactionsSignals:
        pass
```

- Secret management
  - For now, secrets should be included in [dotenv](../huma_signals/dotenv/) and loaded thru [settings](../evaluation_agent/settings.py) when DSP service is initialized.
- Name
  - Each Signal Adapter should have a unique name.
  - The Signal Adapter's name is used as the namespace for signals.
  - For example, a signal's full name looks like `signal_adapter_name.signal_name` so we can avoid name conflict.
- Required inputs
  - These are the inputs a signal adapter required to fetch and compute signals.
  - It's the caller's responsibility to provide these inputs. In most cases, the caller will be the [Huma Evaluation Agent](https://docs.huma.finance/developer-guidlines/evaluation_agent).
- The `fetch` method
  - The unified interface to receive inputs and return computed signals.

### Tests

Please make sure to include extensive tests under [tests](../tests/adapters/).

- We use `pytest` for test framework.
- Make sure to use `pytest-describe` to organize tests.
Please provide the necessary fixtures to properly test the new adapter end-to-end.

## Life cycle of a new Signal Adapter

1. Implement the Signal Adapter according to the provided interface, and submit a pull request for review by Huma DAO.
2. If your Signal Adapter is accepted, it will be deployed on the DSP with the appropriate open-source license.
3. All accepted Signal Adapters will be listed and available for use by Evaluation Agents (EAs).
4. Performance and usage statistics for Signal Adapters will be regularly collected and shared as metadata. This information will be valuable to EA developers in choosing the most robust Signal Adapters, and will also be used to calculate rewards for contributors.
5. Each Signal Adapter must be maintained by its original developer, Huma DAO, or the community. The maintainer will receive rewards but is also responsible for meeting service level agreements, implementing new features, and addressing bug fixes for the Signal Adapter.

## (Coming Soon) Developer participation and rewards

We invite developers to contribute to the initial development and ongoing maintenance of Signal Adapters on the DSP platform. As a way to kickstart development, Huma offers bounty programs and a portion of the protocol revenue will be allocated to reward Signal Adapter developers and maintainers. The Huma DAO will review all contributions and determine how to distribute the reward pool among different contributors. Join us and be a part of building the future of decentralized finance!

# Ethereum Wallet Signal Adapter

This is the repository for the Signal Adapter that fetch signal about Ethereum addresses.

## Type of signals

- Address' tenure
- Address' number of transactions
- Address' current and historical balance
- ...

## Local Development

See [here](../../../docs/getting_started.md) for the development guide.

## Required environment variable

The following environment variable is required to run the adapter.
(Sign up at https://etherscan.io/myapikey to get an API key)

```bash
ETHERSCAN_BASE_URL
ETHERSCAN_API_KEY
```

## Tests

```bash
make test
```

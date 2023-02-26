# Polygon Wallet Signal Adapter

This is the repository for the Signal Adapter that fetch signal about Polygon addresses.

## Type of signals

- Address' tenure
- Address' number of transactions
- Address' current and historical balance
- ...

## Local Development

See [here](../../../docs/getting_started.md) for the development guide.

## Required environment variable

The following environment variable is required to run the adapter.
(Sign up at https://polygonscan.com/myapikey to get an API key)

```bash
POLYGONSCAN_BASE_URL
POLYGONSCAN_API_KEY
```

## Tests

```bash
make test
```

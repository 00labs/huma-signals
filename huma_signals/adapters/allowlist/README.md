# Huma Lending Pool Signal Adapter

This is the repository for the Signal Adapter that fetch signal from Huma lending pool.

## Type of signals

- on-chain pool setting
- pool's EA (underwriter) settings
- pool liquidity
- pool utilization

## Local Development

See [here](../../../docs/getting_started.md) for the development guide.

## Required environment variable

The following environment variable is required to run the adapter

```bash
WEB3_PROVIDER_URL
```

You can get Alchemy keys [here](https://docs.alchemy.com/docs/alchemy-quickstart-guide).

## Tests

```
make test
```

# RequestNetwork Invoice Factoring Signal Adapter

This is the repository for the Signal Adapter that fetch signal RequestNetwork Invoice

## Type of signals

- RequestNetwork Invoice information
- RequestNetwork payer history
- RequestNetwork payee history

## Local Development

See [here](../../../docs/getting_started.md) for the development guide.

## Required environment variable

The following environment variable is required to run the adapter

```bash
CHAIN
REQUEST_NETWORK_SUBGRAPH_ENDPOINT_URL
REQUEST_NETWORK_INVOICE_API_URL
```

## Tests

```bash
make test
```

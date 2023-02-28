# Huma Lending Pool Signal Adapter

This determines whether a borrower is authorized to
borrow from a lending pool given a contract address that implements the following function:
```typescript
function getWhitelistedBorrowers() public view returns (address[] memory);
```

## Type of signals

- if borrower is in the set of authorized borrower addresses 

## Local Development

See [here](../../../docs/getting_started.md) for the development guide.

## Required environment variable

The following environment variable is required to run the adapter

```bash
WEB3_PROVIDER_URL
ETHERSCAN_API_KEY
ETHERSCAN_BASE_URL
```
Keep in mind that the contract abi is pulled from Etherscan.

You can get Alchemy keys [here](https://docs.alchemy.com/docs/alchemy-quickstart-guide).

## Tests

```
make test
```

"""
This file contains real IDs/values from Request.
"""
import pytest


@pytest.fixture
def rn_subgraph_endpoint_url() -> str:
    return "https://api.thegraph.com/subgraphs/name/requestnetwork/request-payments-mainnet"


@pytest.fixture
def from_address() -> str:
    return "0x8d2aa089af73e788cf7afa1f94bf4cf2cde0db61"


@pytest.fixture
def to_address() -> str:
    return "0x63d6287d5b853ccfedba1247fbeb9a40512f709a"  # gitleaks:allow

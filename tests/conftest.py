import os

import pytest

from huma_signals import settings
from huma_signals.commons.chains import Chain

# Fixtures registered below will be made globally available.
pytest_plugins = [
    "tests.fixtures.clients.eth.eth_fixtures",
    "tests.fixtures.clients.polygon.polygon_fixtures",
    "tests.fixtures.clients.request.request_fixtures",
]


@pytest.fixture(scope="session", autouse=True)
def ensure_test_env() -> None:
    """make sure the env is set to TEST"""
    assert os.getenv("ENV") == settings.Env.TEST
    assert os.getenv("CHAIN") == Chain.GOERLI.value

import os

import pytest

from huma_signals import settings


@pytest.fixture(scope="session", autouse=True)
def ensure_test_env() -> None:
    """make sure the env is set to TEST"""
    assert os.getenv("ENV") == settings.Env.TEST

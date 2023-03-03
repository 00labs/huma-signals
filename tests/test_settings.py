import os

from huma_signals import settings
from huma_signals.commons import chains


def describe_settings() -> None:
    def it_defaults_to_test_env() -> None:
        s = settings.Settings()
        assert s.env == settings.Env.TEST

    def it_defaults_to_goerli_chain() -> None:
        s = settings.Settings()
        assert s.chain == chains.Chain.GOERLI

    def it_supports_case_insensitive_env() -> None:
        os.environ["EnV"] = "RANDOM_STRING"
        s = settings.Settings()
        assert s.env == "RANDOM_STRING"

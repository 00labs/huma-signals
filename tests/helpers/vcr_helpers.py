import contextlib
import pathlib
from typing import Any, Iterator

import vcr

VCR_FIXTURES_DIRECTORY = (
    pathlib.Path(__file__).parent.parent / "fixtures" / "vcr_cassettes"
)


@contextlib.contextmanager
def use_cassette(fixture_file_path: str, *args: Any, **kwargs: Any) -> Iterator:
    with vcr.use_cassette(
        f"{VCR_FIXTURES_DIRECTORY}/{fixture_file_path}",
        # The `test` host is where the test server is running in e2e tests.
        # We want the test to make actual requests to the test server, hence
        # ignore them here. We also want to ignore any requests made to QLDB
        # since we want to test the real interactions.
        ignore_hosts=["test"],
        ignore_localhost=True,
        filter_headers=["Authorization", "authorization"],
        *args,
        **kwargs,
    ) as cass:
        yield cass
        assert cass.all_played

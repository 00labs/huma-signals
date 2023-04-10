import contextlib
import pathlib
import re
from typing import Any, Iterator

import vcr
from vcr import cassette, request

VCR_FIXTURES_DIRECTORY = (
    pathlib.Path(__file__).parent.parent / "fixtures" / "vcr_cassettes"
)


@contextlib.contextmanager
def use_cassette(fixture_file_path: str, *args: Any, **kwargs: Any) -> Iterator:
    with vcr.use_cassette(
        f"{VCR_FIXTURES_DIRECTORY}/{fixture_file_path}",
        # The `test` host is where the test server is running in e2e tests.
        # We want the test to make actual requests to the test server, hence
        # ignore them here.
        ignore_hosts=["test"],
        ignore_localhost=True,
        filter_headers=["Authorization", "authorization"],
        *args,
        **kwargs,
    ) as cass:
        yield cass
        assert cass.all_played


def get_requests_for_uri(
    cass: cassette.Cassette, pattern: str
) -> list[request.Request]:
    """
    Returns a list of requests from the cassette where the `uri` matches the given
    pattern
    """
    regex = re.compile(pattern)
    return [r for r in cass.requests if regex.search(r.uri) is not None]


def has_request_for_uri(cass: cassette.Cassette, pattern: str) -> bool:
    """
    Return true if the cassette contains any request where the `uri` matches the given
    pattern, false otherwise
    """
    return len(get_requests_for_uri(cass, pattern)) > 0

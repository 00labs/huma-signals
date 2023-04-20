import contextlib
import pathlib
import re
from typing import Any, Iterator

import vcr
from vcr import cassette, request

VCR_FIXTURES_DIRECTORY = (
    pathlib.Path(__file__).parent.parent / "fixtures" / "vcr_cassettes"
)


def _match_alchemy_url(
    incoming_req: vcr.request.Request, recorded_req: vcr.request.Request
) -> bool:
    # It's an unfortunate fact that Alchemy puts the API key at the end of the URL directly as
    # part of the path, so if whoever runs the test uses a different API key then request matching
    # would fail. So let's not compare the last part of the URL when it's an Alchemy URL.
    if "alchemy.com" in incoming_req.host and "alchemy.com" in recorded_req.host:
        filtered_r1_url = incoming_req.uri[: incoming_req.uri.rfind("/")]
        return filtered_r1_url == recorded_req.uri

    return incoming_req.uri == recorded_req.uri


my_vcr = vcr.VCR()
my_vcr.register_matcher(name="alchemy_url", matcher=_match_alchemy_url)


@contextlib.contextmanager
def use_cassette(fixture_file_path: str, **kwargs: Any) -> Iterator:
    with my_vcr.use_cassette(
        f"{VCR_FIXTURES_DIRECTORY}/{fixture_file_path}",
        # The `test` host is where the test server is running in e2e tests.
        # We want the test to make actual requests to the test server, hence
        # ignore them here.
        ignore_hosts=["test"],
        ignore_localhost=True,
        filter_headers=["Authorization", "authorization"],
        # Some APIs require the sender to include the API key as a query param,
        # so let's filter them out.
        filter_query_parameters=["api_key", "apiKey", "apikey"],
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

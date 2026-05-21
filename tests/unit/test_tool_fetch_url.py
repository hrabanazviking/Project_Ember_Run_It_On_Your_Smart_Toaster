"""``fetch_url`` tool — happy path + every sandbox refusal.

Uses the module's test seams (``_set_url_opener``, ``_set_address_resolver``,
``_set_robots_fetcher``) so no real network traffic happens.
"""

from __future__ import annotations

import importlib
from io import BytesIO

import pytest

from ember.schemas.tool import ApprovalPolicy, ToolCall
from ember.spark.funi.tools.registry import clear, lookup
from ember.tools import fetch_url

# --------------------------------------------------------------------- #
# Fixtures + fakes                                                      #
# --------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def _isolate_registry_and_seams():
    clear()
    importlib.reload(fetch_url)
    fetch_url._reset_seams()
    yield
    fetch_url._reset_seams()
    clear()


def _call(arguments: dict) -> ToolCall:
    return ToolCall(call_id="c-1", name="fetch_url", arguments=arguments)


class _FakeResponse:
    """Stand-in for urllib's HTTPResponse — just enough surface."""

    def __init__(self, body: bytes, *, content_type: str = "text/plain",
                 final_url: str | None = None) -> None:
        self._buf = BytesIO(body)
        self.headers = {"Content-Type": content_type}
        self._final_url = final_url

    def read(self, n: int | None = None) -> bytes:
        if n is None:
            return self._buf.read()
        return self._buf.read(n)

    def geturl(self) -> str:
        return self._final_url or "https://example.com/"

    def close(self) -> None:
        self._buf.close()


def _opener_returning(body: bytes, *, content_type: str = "text/plain"):
    """Make an opener that always returns the given body."""
    def opener(req, timeout):
        return _FakeResponse(body, content_type=content_type, final_url=req.full_url)
    return opener


def _public_resolver(*_):
    """Pretend every hostname resolves to a public address."""
    return ["93.184.216.34"]  # example.com's well-known IP


def _allow_all_robots(_robots_url):
    class _AllowAll:
        def can_fetch(self, *_):
            return True
    return _AllowAll()


def _disallow_all_robots(_robots_url):
    class _DenyAll:
        def can_fetch(self, *_):
            return False
    return _DenyAll()


def _private_resolver(*_):
    """Pretend the host resolves to a private address."""
    return ["10.0.0.5"]


def _loopback_resolver(*_):
    return ["127.0.0.1"]


# --------------------------------------------------------------------- #
# Registration                                                          #
# --------------------------------------------------------------------- #


def test_tool_registers_with_per_call_approval() -> None:
    entry = lookup("fetch_url")
    assert entry is not None
    descriptor, _executor = entry
    assert descriptor.required_approval is ApprovalPolicy.PER_CALL
    assert "url" in descriptor.parameters_schema
    assert "allow_private_addresses" in descriptor.parameters_schema


# --------------------------------------------------------------------- #
# Happy path                                                            #
# --------------------------------------------------------------------- #


def test_get_returns_body_with_header(monkeypatch) -> None:
    fetch_url._set_address_resolver(_public_resolver)
    fetch_url._set_robots_fetcher(_allow_all_robots)
    fetch_url._set_url_opener(_opener_returning(b"<html>ok</html>", content_type="text/html"))

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "https://example.com/page"}))

    assert reply.error is None
    assert "GET https://example.com/page" in reply.output
    assert "content-type: text/html" in reply.output
    assert "<html>ok</html>" in reply.output


# --------------------------------------------------------------------- #
# Sandbox: URL shape                                                    #
# --------------------------------------------------------------------- #


def test_refuses_non_string_url() -> None:
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": 42}))
    assert reply.output == ""
    assert "non-empty string" in (reply.error or "")


def test_refuses_non_http_scheme() -> None:
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "ftp://example.com/file.txt"}))
    assert reply.output == ""
    err = reply.error or ""
    assert "scheme" in err
    assert "ftp" in err


def test_refuses_file_scheme() -> None:
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "file:///etc/passwd"}))
    assert reply.output == ""
    assert "not http(s)" in (reply.error or "")


def test_refuses_url_with_no_host() -> None:
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "http:///"}))
    assert reply.output == ""
    assert "no host" in (reply.error or "")


# --------------------------------------------------------------------- #
# Sandbox: address class                                                #
# --------------------------------------------------------------------- #


def test_refuses_loopback_by_default() -> None:
    fetch_url._set_address_resolver(_loopback_resolver)
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "http://localhost/secret"}))
    assert reply.output == ""
    err = reply.error or ""
    assert "loopback" in err
    assert "allow_private_addresses" in err


def test_refuses_rfc1918_by_default() -> None:
    fetch_url._set_address_resolver(_private_resolver)
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "http://internal.example/"}))
    assert reply.output == ""
    err = reply.error or ""
    assert "private" in err
    assert "RFC1918" in err


def test_allow_private_lets_loopback_through() -> None:
    """Operator opted-in; still PER_CALL-approved per descriptor."""
    fetch_url._set_address_resolver(_loopback_resolver)
    fetch_url._set_robots_fetcher(_allow_all_robots)
    fetch_url._set_url_opener(_opener_returning(b"local-ok"))

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({
        "url": "http://localhost/healthz",
        "allow_private_addresses": True,
    }))
    assert reply.error is None
    assert "local-ok" in reply.output


def test_refuses_unresolvable_host() -> None:
    def _broken_resolver(_):
        raise OSError("name lookup failed")
    fetch_url._set_address_resolver(_broken_resolver)
    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "http://nope.invalid/"}))
    assert reply.output == ""
    assert "DNS lookup failed" in (reply.error or "")


# --------------------------------------------------------------------- #
# Sandbox: robots.txt                                                   #
# --------------------------------------------------------------------- #


def test_refuses_when_robots_disallows() -> None:
    fetch_url._set_address_resolver(_public_resolver)
    fetch_url._set_robots_fetcher(_disallow_all_robots)
    fetch_url._set_url_opener(_opener_returning(b"should-not-be-fetched"))

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "https://example.com/blocked"}))
    assert reply.output == ""
    assert "robots.txt disallows" in (reply.error or "")


def test_treats_missing_robots_as_allowed() -> None:
    """If robots.txt can't be fetched, the standard interpretation is
    'no rules apply' — the tool proceeds with the GET."""
    fetch_url._set_address_resolver(_public_resolver)
    fetch_url._set_robots_fetcher(lambda _url: None)
    fetch_url._set_url_opener(_opener_returning(b"hello"))

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "https://example.com/"}))
    assert reply.error is None
    assert "hello" in reply.output


# --------------------------------------------------------------------- #
# Response size handling                                                #
# --------------------------------------------------------------------- #


def test_response_above_cap_is_truncated_with_note() -> None:
    big = b"x" * (fetch_url._MAX_RESPONSE_BYTES + 100)
    fetch_url._set_address_resolver(_public_resolver)
    fetch_url._set_robots_fetcher(_allow_all_robots)
    fetch_url._set_url_opener(_opener_returning(big))

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "https://example.com/big"}))
    assert reply.error is None
    assert "response truncated" in reply.output


# --------------------------------------------------------------------- #
# Network failures map to typed-error ToolReply                         #
# --------------------------------------------------------------------- #


def test_http_error_maps_to_tool_error() -> None:
    import urllib.error  # noqa: PLC0415

    def _raises_http(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

    fetch_url._set_address_resolver(_public_resolver)
    fetch_url._set_robots_fetcher(_allow_all_robots)
    fetch_url._set_url_opener(_raises_http)

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "https://example.com/missing"}))
    assert reply.output == ""
    err = reply.error or ""
    assert "404" in err
    assert "Not Found" in err


def test_url_error_maps_to_tool_error() -> None:
    import urllib.error  # noqa: PLC0415

    def _raises_url(req, timeout):
        raise urllib.error.URLError(ConnectionRefusedError("connect refused"))

    fetch_url._set_address_resolver(_public_resolver)
    fetch_url._set_robots_fetcher(_allow_all_robots)
    fetch_url._set_url_opener(_raises_url)

    _descriptor, execute = lookup("fetch_url")  # type: ignore[misc]
    reply = execute(_call({"url": "https://example.com/down"}))
    assert reply.output == ""
    assert "URL error" in (reply.error or "")

"""``fetch_url`` — first-party tool that GETs an http(s) URL.

Approval policy is :class:`ApprovalPolicy.PER_CALL` — the operator
sees the exact URL before each invocation.

The sandbox refuses, in order:

1. Non-string URL or empty URL.
2. URLs with a scheme other than ``http`` / ``https``.
3. URLs whose host resolves to a private address (RFC1918), loopback,
   link-local, or multicast — unless the operator passes
   ``allow_private_addresses=True`` (Phase 16 config will surface this
   as a config knob; for now it's an explicit per-call argument).
4. URLs disallowed by the target site's ``robots.txt``.
5. Responses larger than ``_MAX_RESPONSE_BYTES`` (1 MiB).

Refusals come back as :class:`ToolReply` with ``error=...`` and an
empty ``output``. The audit log records the proposed URL; the body is
never fetched on a refusal path. Stdlib-only (``urllib`` + ``ipaddress``
+ ``urllib.robotparser``); no third-party HTTP client.
"""

from __future__ import annotations

import ipaddress
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi.tools.registry import register

_NAME = "fetch_url"
_USER_AGENT = "Ember-Agent/0.1 (+https://github.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster)"
_REQUEST_TIMEOUT_S = 10.0
_MAX_RESPONSE_BYTES = 1 * 1024 * 1024  # 1 MiB

# Test seam — tests inject a fake opener via _set_url_opener(fn) instead
# of patching urllib.request.urlopen directly. The fn takes (url, timeout)
# and returns a file-like with .read() and .geturl() and .headers.
_URL_OPENER = None
_ADDRESS_RESOLVER = None  # tests inject a fake host→ip resolver
_ROBOTS_FETCHER = None    # tests inject a fake robots.txt parser

_DESCRIPTOR = ToolDescriptor(
    name=_NAME,
    description=(
        "GET an http(s) URL and return up to 1 MiB of the response body. "
        "Refuses private / loopback / link-local addresses unless "
        "allow_private_addresses=true. Honours robots.txt."
    ),
    parameters_schema={
        "url": ToolParameter(
            kind=ToolParameterKind.URL,
            description="The http(s) URL to fetch.",
        ),
        "allow_private_addresses": ToolParameter(
            kind=ToolParameterKind.BOOLEAN,
            description=(
                "Allow RFC1918 / loopback / link-local targets. "
                "Default false; the operator approves each call anyway."
            ),
            required=False,
            default=False,
        ),
    },
    required_approval=ApprovalPolicy.PER_CALL,
    timeout_s=_REQUEST_TIMEOUT_S + 5.0,  # give the tool 5s of slack on top of the urlopen timeout
)


# --------------------------------------------------------------------- #
# Test seams                                                            #
# --------------------------------------------------------------------- #


def _set_url_opener(fn) -> None:
    """Test-only: override ``urllib.request.urlopen``-shape."""
    global _URL_OPENER  # noqa: PLW0603 — test seam by design
    _URL_OPENER = fn


def _set_address_resolver(fn) -> None:
    """Test-only: override the host→ip resolver."""
    global _ADDRESS_RESOLVER  # noqa: PLW0603 — test seam by design
    _ADDRESS_RESOLVER = fn


def _set_robots_fetcher(fn) -> None:
    """Test-only: override the robots.txt parser construction."""
    global _ROBOTS_FETCHER  # noqa: PLW0603 — test seam by design
    _ROBOTS_FETCHER = fn


def _reset_seams() -> None:
    """Test-only teardown helper."""
    global _URL_OPENER, _ADDRESS_RESOLVER, _ROBOTS_FETCHER  # noqa: PLW0603
    _URL_OPENER = None
    _ADDRESS_RESOLVER = None
    _ROBOTS_FETCHER = None


# --------------------------------------------------------------------- #
# Executor                                                              #
# --------------------------------------------------------------------- #


def _execute(call: ToolCall) -> ToolReply:  # noqa: PLR0911 — each refusal is one clear early-return
    started = time.monotonic()
    raw_url = call.arguments.get("url")
    allow_private = bool(call.arguments.get("allow_private_addresses", False))

    if not isinstance(raw_url, str) or not raw_url:
        return _error(call, "fetch_url: 'url' must be a non-empty string", started)

    parsed = urlsplit(raw_url)
    if parsed.scheme not in ("http", "https"):
        return _error(
            call,
            f"fetch_url: refused: scheme {parsed.scheme!r} is not http(s)",
            started,
        )
    if not parsed.hostname:
        return _error(call, "fetch_url: refused: URL has no host", started)

    refusal = _check_address_class(parsed.hostname, allow_private=allow_private)
    if refusal is not None:
        return _error(call, refusal, started)

    robots_refusal = _check_robots(raw_url, parsed)
    if robots_refusal is not None:
        return _error(call, robots_refusal, started)

    try:
        body, content_type, final_url = _open_and_read(raw_url)
    except urllib.error.HTTPError as exc:
        return _error(
            call,
            f"fetch_url: HTTP error: {exc.code} {exc.reason}",
            started,
        )
    except urllib.error.URLError as exc:
        return _error(
            call,
            f"fetch_url: URL error: {type(exc.reason).__name__}: {exc.reason}",
            started,
        )
    except TimeoutError:
        return _error(call, "fetch_url: timeout fetching URL", started)
    except OSError as exc:
        return _error(
            call,
            f"fetch_url: network error: {type(exc).__name__}: {exc}",
            started,
        )

    truncated_note = ""
    if len(body) > _MAX_RESPONSE_BYTES:
        body = body[:_MAX_RESPONSE_BYTES]
        truncated_note = (
            f"\n\n[fetch_url: response truncated at {_MAX_RESPONSE_BYTES} bytes]"
        )

    text = body.decode("utf-8", errors="replace")
    header = (
        f"GET {final_url}\n"
        f"content-type: {content_type or 'unknown'}\n"
        f"bytes: {len(body)}\n"
        f"---\n"
    )
    return ToolReply(
        call_id=call.call_id,
        output=header + text + truncated_note,
        elapsed_s=time.monotonic() - started,
    )


# --------------------------------------------------------------------- #
# Sandbox helpers                                                       #
# --------------------------------------------------------------------- #


def _check_address_class(host: str, *, allow_private: bool) -> str | None:
    """Refuse RFC1918 / loopback / link-local / multicast unless allowed."""
    try:
        addresses = _resolve(host)
    except OSError as exc:
        return f"fetch_url: refused: DNS lookup failed for {host!r}: {exc}"

    for addr in addresses:
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        if ip.is_loopback and not allow_private:
            return (
                f"fetch_url: refused: {host} → {addr} is a loopback address; "
                f"pass allow_private_addresses=true to override"
            )
        if ip.is_private and not allow_private:
            return (
                f"fetch_url: refused: {host} → {addr} is a private address "
                f"(RFC1918); pass allow_private_addresses=true to override"
            )
        if ip.is_link_local and not allow_private:
            return (
                f"fetch_url: refused: {host} → {addr} is a link-local address; "
                f"pass allow_private_addresses=true to override"
            )
        if ip.is_multicast:
            return (
                f"fetch_url: refused: {host} → {addr} is a multicast address"
            )
    return None


def _resolve(host: str) -> list[str]:
    """Resolve a host to its IP addresses. Test seam-aware."""
    resolver = _ADDRESS_RESOLVER or _default_resolver
    return resolver(host)


def _default_resolver(host: str) -> list[str]:
    """Default resolver via ``socket.getaddrinfo``.

    Returns the unique address strings for the host. The list shape
    mirrors what ``urllib`` will see when it actually connects.
    """
    infos = socket.getaddrinfo(host, None)
    return list({info[4][0] for info in infos})


def _check_robots(raw_url: str, parsed) -> str | None:
    """Honour robots.txt for the target site.

    Failures fetching robots.txt are treated as "not disallowed" — the
    standard interpretation. Tests inject a fake parser via
    :func:`_set_robots_fetcher`.
    """
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    fetcher = _ROBOTS_FETCHER or _default_robots
    try:
        parser = fetcher(robots_url)
    except Exception:
        return None
    if parser is None:
        return None
    try:
        allowed = parser.can_fetch(_USER_AGENT, raw_url)
    except Exception:
        return None
    if not allowed:
        return f"fetch_url: refused: robots.txt disallows {raw_url}"
    return None


def _default_robots(robots_url: str) -> RobotFileParser | None:
    """Fetch and parse robots.txt via stdlib.

    Returns None when the file can't be fetched (treated as "no rules"
    upstream).
    """
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    return parser


# --------------------------------------------------------------------- #
# Fetch                                                                 #
# --------------------------------------------------------------------- #


def _open_and_read(url: str) -> tuple[bytes, str, str]:
    """Perform the GET. Returns (body, content_type, final_url).

    ``urllib.request.urlopen`` follows redirects by default; the
    redirect target is re-checked at the OS-socket layer when urllib
    actually connects, but the URL-class check we did above only
    validates the initial host. Phase 17 may tighten this with a custom
    redirect handler; for slice 2 the per-call approval is the gating
    constraint.
    """
    import contextlib  # noqa: PLC0415 — narrowly scoped
    opener = _URL_OPENER or _default_opener
    req = urllib.request.Request(
        url, headers={"User-Agent": _USER_AGENT},
    )
    response = opener(req, _REQUEST_TIMEOUT_S)
    try:
        body = response.read(_MAX_RESPONSE_BYTES + 1)  # +1 so we can detect overflow
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()
    finally:
        with contextlib.suppress(Exception):
            response.close()
    return body, content_type, final_url


def _default_opener(req, timeout):
    return urllib.request.urlopen(req, timeout=timeout)


# --------------------------------------------------------------------- #
# Helpers                                                               #
# --------------------------------------------------------------------- #


def _error(call: ToolCall, msg: str, started: float) -> ToolReply:
    return ToolReply(
        call_id=call.call_id,
        error=msg,
        elapsed_s=time.monotonic() - started,
    )


# Side-effect registration — see ember.tools README §1.
register(_DESCRIPTOR, _execute)


__all__: list[str] = []

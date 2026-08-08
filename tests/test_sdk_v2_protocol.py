"""SDK v2 protocol conformance — the §5 matrix, as real tests.

These exist because the port's own guarantees deserve the same CI treatment
1.7.0 gave the validation layer. Every leg here was previously a one-off script;
running them in-process via ``Client(server, mode=...)`` makes them cheap enough
to keep.

SDK v1 has no ``mcp.Client``, so the whole module skips on the 1.x maintenance
branch rather than failing there.

Run with:  pytest tests/test_sdk_v2_protocol.py -v
"""

import asyncio
import importlib.metadata as md
import os
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("USE_MOCK_DATA", "true")

mcp_major = int(md.version("mcp").split(".")[0])
pytestmark = pytest.mark.skipif(
    mcp_major < 2, reason="SDK v2 protocol surface; not present on the 1.x line"
)

if mcp_major >= 2:
    from mcp import Client


def _server():
    import sap_datasphere_mcp_server as srv
    return srv.server


async def _with_client(mode, fn):
    async with Client(_server(), mode=mode) as client:
        return await fn(client)


def _run(mode, fn):
    return asyncio.run(_with_client(mode, fn))


ERAS = ["legacy", "auto"]


# ── Both eras serve the same tool surface (dual-era is the whole point) ──────


@pytest.mark.parametrize("mode", ERAS)
def test_tools_listed_in_both_eras(mode):
    async def go(c):
        return await c.list_tools()
    result = _run(mode, go)
    assert result.tools, f"no tools advertised in {mode} era"


@pytest.mark.parametrize("mode", ERAS)
def test_tools_are_deterministically_ordered(mode):
    """SEP-2549: tools/list SHOULD be deterministically ordered."""
    async def go(c):
        return [t.name for t in (await c.list_tools()).tools]
    names = _run(mode, go)
    assert names == sorted(names)


@pytest.mark.parametrize("mode", ERAS)
def test_resources_and_prompts_served(mode):
    async def go(c):
        return (await c.list_resources()), (await c.list_prompts())
    res, prompts = _run(mode, go)
    assert res.resources, "resources surface lost in the port"
    assert prompts.prompts, "prompts surface lost in the port"


# ── Cache hints (SEP-2549): modern only, by design ───────────────────────────


def test_cache_hints_present_on_modern_era():
    async def go(c):
        return await c.list_tools()
    result = _run("auto", go)
    assert result.ttl_ms > 0, "modern connections must carry ttlMs"
    assert result.cache_scope == "private"


def test_cache_hints_withheld_on_legacy_era():
    """Legacy clients predate the caching SEP and must not be handed hints."""
    async def go(c):
        return await c.list_tools()
    assert _run("legacy", go).ttl_ms == 0


def test_cache_hint_ttl_comes_from_cache_manager():
    """The protocol hint and the internal cache must not drift apart."""
    from cache_manager import CacheCategory, CacheManager
    async def go(c):
        return await c.list_tools()
    expected_ms = CacheManager.DEFAULT_TTL[CacheCategory.TABLE_SCHEMA] * 1000
    assert _run("auto", go).ttl_ms == expected_ms


# ── is_error must reflect the outcome, not merely that a call completed ──────


@pytest.mark.parametrize("mode", ERAS)
def test_successful_call_is_not_flagged_an_error(mode):
    async def go(c):
        return await c.call_tool("list_spaces", {})
    assert _run(mode, go).is_error is False


@pytest.mark.parametrize("mode", ERAS)
def test_validation_failure_is_flagged_an_error(mode):
    """The 1.x handlers report failure in the text, not by raising.

    A naive adapter returns is_error=False for those, so a rejected call looks
    successful to any v2 client that branches on the flag. Pinned here because
    that regression was live during the port.
    """
    async def go(c):
        return await c.call_tool("list_spaces", {"include_details": "not-a-bool"})
    result = _run(mode, go)
    assert result.is_error is True
    assert "Validation" in result.content[0].text


@pytest.mark.parametrize("mode", ERAS)
def test_traversal_rejected_end_to_end(mode):
    """1.7.0's protection must survive the port, over the wire."""
    async def go(c):
        return await c.call_tool("get_space_info", {"space_id": "SPACE/../../admin"})
    result = _run(mode, go)
    assert result.is_error is True


def test_unknown_tool_is_flagged_an_error():
    async def go(c):
        return await c.call_tool("no_such_tool", {})
    assert _run("auto", go).is_error is True


# ── Server identity (the 1.5.2 lesson) ──────────────────────────────────────


def test_server_reports_the_package_version_not_the_sdk_version():
    """HTTP builds its own InitializationOptions from the Server object, so the
    version must be set at construction. Regressing this makes the server
    report the SDK's version as its own."""
    import sap_datasphere_mcp_server as srv
    pkg = md.version("sap-datasphere-mcp")
    assert srv._SERVER_VERSION == pkg
    assert srv.server.version == pkg
    assert srv._build_init_options().server_version == pkg


# ── Tool profiles — the shipped default is a named leg ───────────────────────


@pytest.mark.parametrize(
    "profile,diagnostics,expected",
    [("lean", "false", 39), ("full", "false", 46), ("full", "true", 49)],
)
def test_tool_profile_counts(monkeypatch, profile, diagnostics, expected):
    """lean-39 is the shipped default and must not silently change."""
    monkeypatch.setenv("DATASPHERE_TOOL_PROFILE", profile)
    monkeypatch.setenv("DATASPHERE_EXPOSE_DIAGNOSTICS", diagnostics)
    import sap_datasphere_mcp_server as srv
    tools = asyncio.run(srv.handle_list_tools())
    assert len(tools) == expected


# ── No deprecated surface in our own code paths ─────────────────────────────


def test_no_deprecation_warnings_from_our_code():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        async def go(c):
            await c.list_tools()
            await c.call_tool("list_spaces", {})
        _run("auto", go)
    ours = [
        w for w in caught
        if "sap_datasphere" in str(getattr(w, "filename", ""))
        and issubclass(w.category, DeprecationWarning)
    ]
    assert not ours, [str(w.message) for w in ours]


# ── Dual-era over HTTP, not just in-process ─────────────────────────────────
#
# The era tests above run in-process, which exercises the protocol but not the
# transport. Cross-transport asymmetry is the 1.5.2 lesson: the HTTP path
# builds its own InitializationOptions and once reported the SDK's version as
# the server's. A legacy client arriving over HTTP must still be answered.


@pytest.fixture(scope="module")
def http_server():
    import socket
    import subprocess
    import time as _time
    import urllib.request

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    proc = subprocess.Popen(
        [sys.executable, "-m", "sap_datasphere_mcp_server",
         "--transport", "http", "--host", "127.0.0.1", "--port", str(port)],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
        env={**os.environ, "USE_MOCK_DATA": "true"},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            urllib.request.urlopen(base + "/health", timeout=1).read()
            break
        except Exception:
            _time.sleep(0.5)
    else:
        proc.terminate()
        pytest.skip("HTTP transport did not come up (starlette/uvicorn missing?)")
    yield base
    proc.terminate()
    proc.wait(timeout=10)


def _post(base, body, headers=None):
    import json as _json
    import urllib.request
    req = urllib.request.Request(
        base + "/mcp/", data=_json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return _json.loads(resp.read().decode())


def test_legacy_client_over_http_is_answered(http_server):
    """Dual-era must hold on HTTP too, not only on stdio.

    A legacy client sends `initialize` with none of the 2026-07-28 envelope
    headers. Rejecting it here would break every 2025-era client that connects
    over HTTP while stdio kept working -- precisely the asymmetry 1.5.2 taught.
    """
    reply = _post(http_server, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                   "clientInfo": {"name": "legacy-http", "version": "0"}},
    })
    assert "error" not in reply, reply
    assert reply["result"]["serverInfo"]["name"] == "sap-datasphere-mcp"


def test_http_reports_the_package_version(http_server):
    """The HTTP path builds its own InitializationOptions from the Server
    object; this is the transport where the version regression appeared."""
    reply = _post(http_server, {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                   "clientInfo": {"name": "legacy-http", "version": "0"}},
    })
    assert reply["result"]["serverInfo"]["version"] == md.version("sap-datasphere-mcp")


def test_modern_client_over_http_gets_cache_hints(http_server):
    """Modern era on HTTP must carry ttlMs/cacheScope (SEP-2549)."""
    reply = _post(
        http_server,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list",
         "params": {"_meta": {
             "io.modelcontextprotocol/protocolVersion": "2026-07-28",
             "io.modelcontextprotocol/clientCapabilities": {}}}},
        headers={"MCP-Protocol-Version": "2026-07-28", "Mcp-Method": "tools/list"},
    )
    result = reply["result"]
    assert result["ttlMs"] > 0
    assert result["cacheScope"] == "private"
    names = [t["name"] for t in result["tools"]]
    assert names == sorted(names)


# ── Capability layer ────────────────────────────────────────────────────────


def test_countability_read_from_metadata_annotation():
    """Declarative capability, using the shapes seen on the live tenant."""
    import asset_capability as ac
    analytical = (
        '<Annotations Target="X/Y"><Annotation Term="Capabilities.CountRestrictions">'
        '<Record Type="Capabilities.CountRestrictionsType">'
        '<PropertyValue Property="Countable" Bool="false"/></Record></Annotation></Annotations>'
    )
    assert ac.countability_from_metadata(analytical) is False
    # Relational assets declared no CountRestrictions at all in an 80-asset scan.
    assert ac.countability_from_metadata("<Annotations/>") is None


def test_lineage_verdict_is_memoized_per_asset():
    import asset_capability as ac
    from cache_manager import CacheManager
    cache = CacheManager(max_size=50)
    assert ac.is_lineage_limited(cache, "S", "A") is False
    ac.record_filter_profile(cache, "S", "A", ac.FILTER_LINEAGE_LIMITED)
    assert ac.is_lineage_limited(cache, "S", "A") is True
    assert ac.is_lineage_limited(cache, "S", "B") is False, "verdict leaked across assets"


def test_capability_descriptor_survives_a_cache_round_trip():
    import asset_capability as ac
    from cache_manager import CacheManager
    cache = CacheManager(max_size=50)
    ac.record_countable(cache, "SCM_BUSINESS", "OPEN_PO_DETAIL", False)
    cap = ac.get(cache, "SCM_BUSINESS", "OPEN_PO_DETAIL")
    assert cap.countable is False
    assert cap.source["countable"] == "declarative"
    assert cap.discovered_at > 0


def test_lineage_verdict_deflects_once_then_self_heals():
    """A remembered verdict must actually be consulted -- and must not stick.

    Recording without reading delivers nothing; reading without clearing means
    one wrong inference blocks valid filters for the cache lifetime. Clearing
    on read caps the cost of a bad inference at a single deflected call.
    """
    import asset_capability as ac
    from cache_manager import CacheManager
    cache = CacheManager(max_size=50)

    assert ac.consume_lineage_verdict(cache, "S", "A") is False   # nothing known
    ac.record_filter_profile(cache, "S", "A", ac.FILTER_LINEAGE_LIMITED)
    assert ac.consume_lineage_verdict(cache, "S", "A") is True    # deflects
    assert ac.consume_lineage_verdict(cache, "S", "A") is False   # self-healed
    assert ac.is_lineage_limited(cache, "S", "A") is False


def test_bare_400_does_not_brand_an_asset_lineage_limited():
    """Deciding an asset is lineage-limited is a claim we remember, so it needs
    better evidence than any failed request."""
    import sap_datasphere_mcp_server as srv
    assert srv._looks_like_filter_capability_rejection(
        Exception("400 Bad Request: $filter option not supported")) is True
    assert srv._looks_like_filter_capability_rejection(
        Exception("400 Bad Request: malformed entity key")) is False

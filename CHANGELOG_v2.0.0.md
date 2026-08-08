# Changelog - v2.0.0 (MCP Python SDK v2 / 2026-07-28 stateless spec)

**Release Date:** 2026-08-08 · **Base:** 1.7.0 (`0e2afc9`)

The package major changes because the **dependency floor** does:
`mcp>=1.28,<2` becomes `mcp>=2.0,<3`. Package major now tracks SDK major —
**1.x ⇒ SDK 1.x, 2.x ⇒ SDK 2.x** — so the support matrix needs no table to
read. `1.x` continues as a maintenance line for environments that cannot
install SDK 2.x.

**This is not a behavioural rewrite.** Every tool behaves as it did in 1.7.0;
the 142 tests written on the 1.x line pass unchanged here, which was their
purpose.

---

## The port

### Handlers move to constructor kwargs

SDK 2.0.0 removed the decorator API on the low-level `Server`. Handlers are now
supplied as `on_list_tools` / `on_call_tool` / `on_list_resources` /
`on_read_resource` / `on_list_prompts` / `on_get_prompt`, each shaped
`(ctx, params) -> FullResultType`.

**Divergence from the port spec, recorded per its standing rule:** the spec
implies rewriting handlers to build `CallToolResult` directly.
`handle_call_tool` is ~7,000 lines with **230** `return [TextContent(...)]`
sites, each an error path covered by 1.6.0/1.7.0 tests. Rewriting all of them
would put a very large diff through exactly the surface where this project has
twice found silent breakage. Instead each of the six surfaces gets **one thin
adapter**; the dispatch body is byte-identical, and the v2 contract lives in
six places rather than 230.

The low-level `Server` was kept over the new high-level `MCPServer`, as the
spec decided: the centralized dispatch maps 1:1 onto `on_call_tool`, whereas
`MCPServer` would mean decomposing 45 tools into individual registrations for
no gain.

### `is_error` now reflects the outcome

Worth calling out because the first version of the adapter got it wrong. The
1.x handlers signal failure *inside the content text* — `>>> Input Validation
Error <<<` and similar — rather than by raising. In 1.x that was the entire
contract. In v2, `is_error` is a protocol field clients branch on, so an
adapter that always reported `is_error=False` made a **rejected call look
successful**.

Failure is now derived from those banners, with `>>> No Assets Found <<<`
deliberately excluded: the query ran and matched nothing, which is an empty
result rather than a fault. The classifier is conservative — anything not
recognisably a failure stays `is_error=False`, since wrongly flagging a good
result is worse than leaving an unusual error unflagged.

`Confirmation Required` and `User Consent Required` currently count as errors,
on the reasoning that the requested work did not happen. That is a judgement
call and is flagged as such.

### Cache hints (SEP-2549)

`tools/list`, `prompts/list` and `resources/list` carry `ttlMs` and
`cacheScope`. TTL is read from `CacheManager.DEFAULT_TTL` rather than written
as a literal, so the protocol hint and the internal cache cannot drift apart —
which is the only reason to source it from `CacheManager` at all.

`cacheScope` is always `private`: every result is shaped by the tenant OAuth
context this process holds, so a shared gateway must never re-serve one user's
response to another. `tools/list` is deterministically ordered.

Hints are sent to **modern** clients only. Verified on both transports: a
legacy connection sees `ttlMs=0`, a modern one sees `ttlMs=1800000`.

### Per-asset capability layer

1.6.0 established that Datasphere capability varies **per asset, not per
tenant**, discoverable two different ways. Both are now used:

| Path | How | Consumer in this release |
|---|---|---|
| Declarative | reading `$metadata` before the request | `$count` decided by the asset's `Capabilities.CountRestrictions` annotation, replacing the blanket "never on analytical" rule |
| Empirical | interpreting a failure | the lineage-gated filter verdict is memoized per asset instead of rediscovered per call |

Descriptors are keyed `(space_id, asset_id)` and live in the internal
`CacheManager` — **not** the protocol cache, whose `cacheScope` is a two-valued
literal about proxy-cacheability and cannot hold anything of the sort. The
countability read fails **open**: a wrong `$count` costs one failed request,
whereas suppressing it silently returns a page count where a total was asked
for.

The lineage verdict is **consulted, then cleared**. Recording without reading
delivers nothing; reading without clearing means one wrong inference blocks
valid filters for the cache lifetime. Clearing on read caps the cost of a bad
inference at a single deflected call, after which the next attempt goes to the
wire normally. Recording also requires the error to actually implicate a filter
or query option -- a bare 400 is not evidence enough for a claim we then
remember.

Deliberately minimal — two consumers, no speculative fields, no tenant-wide
pre-warming.

### Wire surface and dependencies

`inputSchema` → `input_schema` (49 sites) and `mimeType` → `mime_type` (5).
`McpError` did not appear in this codebase at all. `mcp.types` still imports,
backed by the separate `mcp-types` distribution, so no import paths were
rewritten. The deprecated `LoggingLevel` import is gone. The unused
`httpx>=0.27.0` pin is removed — this codebase imports `requests` and
`aiohttp`, and the SDK now brings `httpx2`.

Unchanged, as verified: `stdio_server()`, `server.run()`,
`InitializationOptions`, `NotificationOptions`, `StreamableHTTPSessionManager`
with its `stateless` / `json_response` flags — so the stateless-HTTP default
and the `--stateful` escape hatch from 1.5.2 both survive.

---

## Tests

`tests/test_sdk_v2_protocol.py` — 29 new cases covering both eras: tool
surface, deterministic ordering, cache hints present on modern and withheld on
legacy, `is_error` fidelity, end-to-end traversal rejection, the three tool
profiles (**lean-39 is the shipped default**), server version identity, absence
of deprecation warnings from our own code, dual-era over HTTP (not only
in-process), and the capability layer. The module
skips cleanly on SDK 1.x so the same suite runs on the maintenance branch.

* **SDK v2:** 171 passed (142 forward-ported + 29 new)
* **SDK 1.x branch:** 142 passed, 29 skipped — unchanged from 1.7.0

---

## Upgrading

`pip install --upgrade sap-datasphere-mcp` gets you 2.0.0. **No client changes
are needed**: the v2 server answers the legacy `initialize` handshake as well
as `server/discover`, so 2025-era clients keep working.

If your environment cannot install SDK 2.x:

```bash
pip install 'sap-datasphere-mcp<2'
```

---

## Known / deferred

* `sap_datasphere_mcp_simple.py` still uses the v1 decorator API and is
  therefore broken under SDK 2.x. It is not in `py-modules`, is not shipped in
  the wheel, and nothing imports it — left in place rather than silently
  deleted or repaired.
* Live-tenant smoke **was** run against 2.0.0 on `partstown-1` with the rotated
  credential: relational and analytical reads, and both capability consumers.
  The countability annotation read returned `False` from the live analytical
  `$metadata` and `None` (countable) from the relational one, confirming the
  asymmetry is per-asset rather than per-path. The lineage read-side path is
  exercised by unit tests but has **not** met a genuinely federated asset --
  none exists on this tenant.
* `NON_FILTERABLE_TYPES` redesign and the `Edm.DateTimeOffset`/`Boolean`/`Guid`
  literal probes remain 1.x hardening, not port scope.
* Tasks extension (SEP-2663) is not in SDK 2.0.0 and was not built against.

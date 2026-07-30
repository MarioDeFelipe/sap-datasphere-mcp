# Changelog - v1.5.2 (P0: pin MCP SDK to the v1 line)

**Release Date:** 2026-07-30

## Critical: fresh installs have been broken since 2026-07-28

The MCP Python SDK released **2.0.0 on 2026-07-28**, alongside the final
2026-07-28 MCP specification. SDK 2.0.0 removes the decorator API on the
low-level `Server` class, which this server is built on:

```
AttributeError: 'Server' object has no attribute 'list_resources'
    at sap_datasphere_mcp_server.py:140
```

Our published package declared `mcp>=1.2.0` with **no upper bound**, so pip
began resolving `mcp==2.0.0` the moment it landed. The npm wrapper's
`postinstall` runs `pip install --upgrade sap-datasphere-mcp`, so every
install or reinstall since July 28 pulled SDK v2 and crashed at import time.

`1.5.2` pins the dependency to the SDK v1 maintenance line:

```toml
dependencies = [
    "mcp>=1.28,<2",
    ...
]
```

`requirements.txt` is pinned to match (it had drifted further, at
`mcp>=0.9.0`). SDK **1.29.0** (also released 2026-07-28) is the current v1
maintenance release and runs this server unchanged.

### If you installed between 2026-07-28 and 2026-07-30

```bash
pip install --upgrade sap-datasphere-mcp
```

Or, if you pin the SDK yourself:

```bash
pip install 'mcp>=1.28,<2'
```

### Scope

This is a dependency pin, not a port. All six low-level handlers
(`list_resources`, `read_resource`, `list_prompts`, `get_prompt`,
`list_tools`, `call_tool`) are unchanged. The SDK v2 port is tracked
separately.

---

## Also in this release

### HTTP transport now defaults to stateless

`_run_http()` previously ran the Streamable HTTP transport with
`json_response=False, stateless=False`. It now defaults to
`json_response=True, stateless=True`.

This server exposes no sampling, no elicitation, and no roots, makes no
server-initiated requests, and never touches `request_context` — and its
consent and cache state is **process-global**, keyed by tool name and user
id rather than by MCP session. Nothing depended on a pinned session, so
stateless is both correct and cheaper to operate behind a load balancer.

The previous behaviour is one flag away:

```bash
sap-datasphere-mcp --transport http --stateful
```

### Reported server version no longer drifts

`_build_init_options()` hardcoded `server_version="1.1.0"` — four releases
stale. It now reads the installed distribution version via
`importlib.metadata`, falling back to `0.0.0-dev` for source checkouts, so
clients see the version they actually installed.

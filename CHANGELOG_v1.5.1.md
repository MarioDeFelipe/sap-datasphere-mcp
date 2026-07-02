# Changelog - v1.5.1 (packaging hotfix)

**Release Date:** 2026-07-02

## Hotfix: include `odata_v4_annotations` in the published wheel

`1.5.0` shipped a broken wheel: the new `odata_v4_annotations` module
introduced by the OData V4 metadata-parser fix was **not listed in**
`[tool.setuptools] py-modules` in `pyproject.toml`, so setuptools omitted
it from the wheel. Every install of `1.5.0` therefore crashed at startup
with:

```
ModuleNotFoundError: No module named 'odata_v4_annotations'
    at sap_datasphere_mcp_server.py:49
```

MCP clients saw `-32000: Connection closed` ~1.8 s after launch.

`1.5.1` is that one-line fix — the module is now listed in
`py-modules` and the built wheel contains it. There is **no functional
change vs 1.5.0**; the parser logic and behaviour are identical.

## Regression guard added

The unit tests pass against source, so they can't catch a wheel-packaging
omission. `.github/workflows/publish.yml` now runs a clean-venv import
smoke test on the built wheel before `twine upload`:

```yaml
- name: Smoke-test built wheel (clean env import)
  run: |
    python -m venv /tmp/smoke
    /tmp/smoke/bin/pip install dist/*.whl
    /tmp/smoke/bin/python -c "import sap_datasphere_mcp_server; import odata_v4_annotations; print('wheel import OK')"
```

Any future missing-module regression fails the release job before it
publishes.

## Users on 1.5.0

`1.5.0` has been yanked / deprecated on PyPI and npm — reinstall to pick
up `1.5.1`. The npm wrapper's `postinstall` `pip install --upgrade
sap-datasphere-mcp` will pull the fixed Python package automatically.

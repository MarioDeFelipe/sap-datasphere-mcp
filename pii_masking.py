"""
pii_masking.py — Config-driven PII / sensitive-field masking layer.

Loaded once at server startup; applied to every data-returning tool response
before the result is serialised to the MCP client.  Fail-closed: if the policy
file is configured but cannot be parsed, the module raises on import so the
server never starts with masking silently disabled.

Environment variables
---------------------
DATASPHERE_PII_POLICY
    Path to a YAML or JSON policy file.  When unset, masking is off (backwards-
    compatible default).

DATASPHERE_PII_MODE
    ``enforce``   – mask values before returning them (default when policy present).
    ``audit_only`` – log what *would* be masked but pass data through unchanged.
    ``off``        – disable masking entirely (same as no policy file).

DATASPHERE_PII_SALT
    Stable secret string used as a prefix for SHA-256 hashing and tokenisation.
    Required whenever any rule uses ``hash`` or ``tokenize``; treated as a secret
    and never logged.
"""

import fnmatch
import hashlib
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger("pii")

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

Action = str  # 'redact' | 'drop' | 'hash' | 'partial:N' | 'tokenize'


class Policy:
    """Parsed representation of a pii_policy.yaml / pii_policy.json file."""

    def __init__(self, cfg: Dict[str, Any], salt: str) -> None:
        # DATASPHERE_PII_MODE overrides the file-level ``mode`` key.
        env_mode = os.getenv("DATASPHERE_PII_MODE", "").strip()
        self.mode: str = env_mode if env_mode else cfg.get("mode", "enforce")

        self.default_action: Action = cfg.get("default_action", "redact")
        self.rules: List[Dict[str, Any]] = cfg.get("rules") or []
        self.allowlist: Dict[str, Any] = cfg.get("allowlist") or {}
        self.salt: str = salt

        # Pre-compile value-pattern regexes.
        raw_patterns: Dict[str, str] = cfg.get("patterns") or {}
        self.patterns: Dict[str, re.Pattern] = {
            name: re.compile(pattern) for name, pattern in raw_patterns.items()
        }


# ---------------------------------------------------------------------------
# Module-level singleton — loaded once at import time.
# ---------------------------------------------------------------------------

def load_policy() -> Optional[Policy]:
    """
    Load and parse the PII policy file referenced by ``DATASPHERE_PII_POLICY``.

    Returns ``None`` when the env var is unset (masking disabled — back-compat).
    Raises ``RuntimeError`` when the env var *is* set but the file cannot be
    read or parsed (fail-closed: server must not start with broken masking).
    """
    path = os.getenv("DATASPHERE_PII_POLICY", "").strip()
    if not path:
        return None

    try:
        with open(path) as fh:
            if path.endswith((".yaml", ".yml")):
                try:
                    import yaml  # type: ignore
                except ImportError as exc:
                    raise RuntimeError(
                        "DATASPHERE_PII_POLICY is set to a YAML file but 'PyYAML' "
                        "is not installed.  Run: pip install PyYAML"
                    ) from exc
                cfg = yaml.safe_load(fh)
            else:
                cfg = json.load(fh)
    except (OSError, IOError) as exc:
        raise RuntimeError(
            f"[pii_masking] Cannot open policy file '{path}': {exc}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            f"[pii_masking] Policy file '{path}' is not valid YAML/JSON: {exc}"
        ) from exc

    if not isinstance(cfg, dict):
        raise RuntimeError(
            f"[pii_masking] Policy file '{path}' must contain a YAML/JSON object at the top level."
        )

    salt = os.getenv("DATASPHERE_PII_SALT", "")
    policy = Policy(cfg, salt)

    log.info(
        "[pii_masking] Policy loaded from '%s' — mode=%s default_action=%s "
        "rules=%d patterns=%d allowlist_enabled=%s",
        path,
        policy.mode,
        policy.default_action,
        len(policy.rules),
        len(policy.patterns),
        policy.allowlist.get("enabled", False),
    )
    return policy


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _apply_action(action: Action, value: Any, salt: str) -> Any:
    """Apply a single masking action to *value*.  Returns the transformed value."""
    if value is None:
        return None
    s = str(value)

    if action == "redact":
        return "***"

    if action == "drop":
        # Sentinel — caller must delete the key rather than store this.
        return "__DROP__"

    if action == "hash":
        return hashlib.sha256((salt + ":" + s).encode()).hexdigest()

    if action.startswith("partial:"):
        try:
            n = int(action.split(":", 1)[1])
        except (ValueError, IndexError):
            n = 4  # Sensible default if mis-configured.
        masked_len = max(0, len(s) - n)
        return ("*" * masked_len) + s[-n:] if n > 0 else "***"

    if action == "tokenize":
        digest = hashlib.sha256((salt + ":" + s).encode()).hexdigest()
        return "TKN_" + digest[:8]

    # Unknown action — treat as redact (fail-closed).
    log.warning("[pii_masking] Unknown action '%s' — falling back to redact.", action)
    return "***"


def _resolve_column_action(
    policy: Policy,
    space: str,
    asset: str,
    column: str,
) -> Optional[Action]:
    """
    Walk the rules list and return the action for *column* in *space/asset*.

    Precedence (highest to lowest):
      1. space-specific AND asset-specific rule with exact column name
      2. space-specific rule with exact column name
      3. global (space='*') rule with exact column name
      4. same but with glob pattern on column name
    Returns ``None`` when no rule matches.
    """
    best_spec: int = -1
    best_action: Optional[Action] = None

    for rule in policy.rules:
        rule_space = rule.get("space", "*")
        rule_asset = rule.get("asset", "*")

        # Space filter (exact match or wildcard).
        if rule_space != "*" and rule_space != space:
            continue
        # Asset filter (exact match or wildcard).
        if rule_asset != "*" and rule_asset != asset:
            continue

        for pattern, action in (rule.get("columns") or {}).items():
            if fnmatch.fnmatch(column.upper(), pattern.upper()):
                # Specificity: 1 point each for non-wildcard space, asset, column.
                spec = (
                    int(rule_space != "*")
                    + int(rule_asset != "*")
                    + int("*" not in pattern)
                )
                if spec > best_spec:
                    best_spec = spec
                    best_action = action

    return best_action


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_masking(
    rows: List[Dict[str, Any]],
    space_id: str,
    asset_id: str,
    policy: Optional[Policy],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Apply the PII policy to *rows* and return ``(masked_rows, masked_field_names)``.

    Parameters
    ----------
    rows:
        List of flat dicts (one per record).  Nested structures are left as-is
        unless a column rule or value pattern matches a top-level key.
    space_id:
        SAP Datasphere space identifier (e.g. ``ZDCS_08``).
    asset_id:
        Asset / table identifier within the space (e.g. ``ZR_SAP_CUSTOMER``).
    policy:
        ``Policy`` instance from ``load_policy()``, or ``None`` to skip masking.

    Returns
    -------
    masked_rows:
        New list of dicts with values transformed according to the policy.
    masked_field_names:
        Sorted list of column names that were touched by the policy (for audit
        logging and the MCP response ``masked_fields`` annotation).
    """
    if policy is None or policy.mode == "off" or not rows:
        return rows, []

    audit_only: bool = (policy.mode == "audit_only")

    # Build allowlist for this specific asset (space.asset compound key).
    asset_key = f"{space_id}.{asset_id}"
    allowed_columns: Optional[List[str]] = None
    if policy.allowlist.get("enabled"):
        allowed_columns = (policy.allowlist.get("assets") or {}).get(asset_key)

    touched: set = set()
    out: List[Dict[str, Any]] = []

    for row in rows:
        new_row: Dict[str, Any] = {}

        for col, val in row.items():
            # ── 1. Allowlist enforcement ──────────────────────────────────────
            if allowed_columns is not None and col not in allowed_columns:
                touched.add(col)
                if not audit_only:
                    # Drop column — do not include in output row.
                    continue

            # ── 2. Column rule ────────────────────────────────────────────────
            action = _resolve_column_action(policy, space_id, asset_id, col)
            new_val = val

            if action:
                touched.add(col)
                if not audit_only:
                    new_val = _apply_action(action, val, policy.salt)
                    if new_val == "__DROP__":
                        # ``drop`` action: exclude the column entirely.
                        continue

            # ── 3. Value-pattern scan (strings only, best-effort secondary net) ─
            elif isinstance(val, str):
                for _name, rx in policy.patterns.items():
                    if rx.search(val):
                        touched.add(col)
                        if not audit_only:
                            new_val = _apply_action(policy.default_action, val, policy.salt)
                        break

            new_row[col] = new_val

        out.append(new_row)

    masked_field_names = sorted(touched)

    # ── Audit log ─────────────────────────────────────────────────────────────
    # Never log raw values — only field names, counts, and mode.
    log.info(
        "[pii_masking] space=%s asset=%s rows=%d masked_fields=%s mode=%s",
        space_id,
        asset_id,
        len(rows),
        masked_field_names,
        policy.mode,
    )

    return out, masked_field_names

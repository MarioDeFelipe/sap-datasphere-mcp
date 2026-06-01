"""
Unit tests for pii_masking.py

Run with:  pytest tests/test_pii_masking.py -v
"""
import hashlib
import os
import sys
import textwrap
import tempfile
import pytest

# Ensure repo root is on sys.path so we can import pii_masking directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pii_masking import Policy, load_policy, apply_masking, _apply_action, _resolve_column_action


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

SALT = "test-salt-abc123"

MINIMAL_CFG: dict = {
    "mode": "enforce",
    "default_action": "redact",
    "rules": [],
    "allowlist": {},
    "patterns": {},
}


def make_policy(**overrides) -> Policy:
    cfg = {**MINIMAL_CFG, **overrides}
    return Policy(cfg, SALT)


def sha256(val: str) -> str:
    return hashlib.sha256((SALT + ":" + val).encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# _apply_action
# ─────────────────────────────────────────────────────────────────────────────

class TestApplyAction:
    def test_redact(self):
        assert _apply_action("redact", "hello@example.com", SALT) == "***"

    def test_redact_none(self):
        assert _apply_action("redact", None, SALT) is None

    def test_drop_sentinel(self):
        assert _apply_action("drop", "anything", SALT) == "__DROP__"

    def test_hash_deterministic(self):
        h1 = _apply_action("hash", "alice", SALT)
        h2 = _apply_action("hash", "alice", SALT)
        assert h1 == h2
        assert h1 == sha256("alice")

    def test_hash_different_values(self):
        assert _apply_action("hash", "alice", SALT) != _apply_action("hash", "bob", SALT)

    def test_partial_keeps_last_n(self):
        result = _apply_action("partial:4", "1234567890", SALT)
        assert result.endswith("7890")
        assert result.startswith("******")

    def test_partial_short_value(self):
        result = _apply_action("partial:6", "abc", SALT)
        # len("abc") = 3 < 6 — no leading asterisks, full value returned
        assert result == "abc"

    def test_tokenize_deterministic(self):
        t1 = _apply_action("tokenize", "IBAN12345", SALT)
        t2 = _apply_action("tokenize", "IBAN12345", SALT)
        assert t1 == t2
        assert t1.startswith("TKN_")
        assert len(t1) == len("TKN_") + 8

    def test_tokenize_different_values(self):
        assert _apply_action("tokenize", "A", SALT) != _apply_action("tokenize", "B", SALT)

    def test_unknown_action_falls_back_to_redact(self):
        assert _apply_action("obfuscate", "value", SALT) == "***"


# ─────────────────────────────────────────────────────────────────────────────
# _resolve_column_action — precedence
# ─────────────────────────────────────────────────────────────────────────────

class TestResolveColumnAction:
    """Most-specific rule wins: asset-level > space-level > global > glob."""

    BASE_RULES = [
        # Global glob
        {"space": "*", "columns": {"*EMAIL*": "redact"}},
        # Space-level exact
        {"space": "SPACE1", "columns": {"EMAIL": "hash"}},
        # Asset-level exact (most specific)
        {"space": "SPACE1", "asset": "TABLE_A", "columns": {"EMAIL": "drop"}},
    ]

    def _policy(self):
        return make_policy(rules=self.BASE_RULES)

    def test_asset_level_wins(self):
        p = self._policy()
        assert _resolve_column_action(p, "SPACE1", "TABLE_A", "EMAIL") == "drop"

    def test_space_level_wins_over_global(self):
        p = self._policy()
        # Different asset — space rule applies, not asset rule
        assert _resolve_column_action(p, "SPACE1", "OTHER_TABLE", "EMAIL") == "hash"

    def test_global_glob_applies_to_other_space(self):
        p = self._policy()
        assert _resolve_column_action(p, "SPACE2", "ANY_TABLE", "MY_EMAIL_ADDR") == "redact"

    def test_no_match_returns_none(self):
        p = self._policy()
        assert _resolve_column_action(p, "SPACE2", "ANY_TABLE", "AMOUNT") is None

    def test_glob_pattern_case_insensitive(self):
        p = make_policy(rules=[{"space": "*", "columns": {"*iban*": "tokenize"}}])
        assert _resolve_column_action(p, "S", "T", "MY_IBAN_CODE") == "tokenize"


# ─────────────────────────────────────────────────────────────────────────────
# apply_masking — integration
# ─────────────────────────────────────────────────────────────────────────────

ROWS = [
    {"NAME": "Alice Smith", "EMAIL": "alice@example.com", "AMOUNT": 100},
    {"NAME": "Bob Jones",  "EMAIL": "bob@example.com",   "AMOUNT": 200},
]


class TestApplyMasking:
    # ── No policy → passthrough ──────────────────────────────────────────────

    def test_no_policy_passthrough(self):
        result, masked = apply_masking(ROWS, "S", "T", None)
        assert result == ROWS
        assert masked == []

    def test_mode_off_passthrough(self):
        p = make_policy(mode="off")
        result, masked = apply_masking(ROWS, "S", "T", p)
        assert result == ROWS
        assert masked == []

    def test_empty_rows_passthrough(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "redact"}}])
        result, masked = apply_masking([], "S", "T", p)
        assert result == []
        assert masked == []

    # ── redact ───────────────────────────────────────────────────────────────

    def test_redact_column(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "redact"}}])
        result, masked = apply_masking(ROWS, "S", "T", p)
        assert all(row["EMAIL"] == "***" for row in result)
        assert "EMAIL" in masked

    # ── drop ─────────────────────────────────────────────────────────────────

    def test_drop_column(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "drop"}}])
        result, masked = apply_masking(ROWS, "S", "T", p)
        assert all("EMAIL" not in row for row in result)
        assert "EMAIL" in masked

    def test_drop_does_not_affect_other_columns(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "drop"}}])
        result, _ = apply_masking(ROWS, "S", "T", p)
        assert all("NAME" in row and "AMOUNT" in row for row in result)

    # ── hash ─────────────────────────────────────────────────────────────────

    def test_hash_column_deterministic(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "hash"}}])
        result1, _ = apply_masking(ROWS, "S", "T", p)
        result2, _ = apply_masking(ROWS, "S", "T", p)
        assert result1[0]["EMAIL"] == result2[0]["EMAIL"]

    def test_hash_does_not_expose_original(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "hash"}}])
        result, _ = apply_masking(ROWS, "S", "T", p)
        assert "alice@example.com" not in result[0]["EMAIL"]
        assert len(result[0]["EMAIL"]) == 64  # SHA-256 hex

    # ── partial ──────────────────────────────────────────────────────────────

    def test_partial_keeps_suffix(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "partial:4"}}])
        result, _ = apply_masking(ROWS, "S", "T", p)
        assert result[0]["EMAIL"].endswith(".com")

    # ── tokenize ─────────────────────────────────────────────────────────────

    def test_tokenize_stable(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "tokenize"}}])
        r1, _ = apply_masking(ROWS, "S", "T", p)
        r2, _ = apply_masking(ROWS, "S", "T", p)
        assert r1[0]["EMAIL"] == r2[0]["EMAIL"]
        assert r1[0]["EMAIL"].startswith("TKN_")

    # ── audit_only mode ──────────────────────────────────────────────────────

    def test_audit_only_passes_data_through(self):
        p = make_policy(mode="audit_only", rules=[{"space": "*", "columns": {"EMAIL": "redact"}}])
        result, masked = apply_masking(ROWS, "S", "T", p)
        # Values unchanged
        assert result[0]["EMAIL"] == "alice@example.com"
        # But field name reported
        assert "EMAIL" in masked

    # ── allowlist ────────────────────────────────────────────────────────────

    def test_allowlist_drops_non_listed_columns(self):
        p = make_policy(allowlist={
            "enabled": True,
            "assets": {"MYSPACE.MYTABLE": ["AMOUNT"]},
        })
        result, masked = apply_masking(ROWS, "MYSPACE", "MYTABLE", p)
        assert all(list(row.keys()) == ["AMOUNT"] for row in result)
        assert "NAME" in masked
        assert "EMAIL" in masked

    def test_allowlist_not_applied_to_other_asset(self):
        p = make_policy(allowlist={
            "enabled": True,
            "assets": {"MYSPACE.MYTABLE": ["AMOUNT"]},
        })
        result, masked = apply_masking(ROWS, "MYSPACE", "OTHER", p)
        # No allowlist for MYSPACE.OTHER → all columns pass through
        assert all("NAME" in row and "EMAIL" in row for row in result)

    def test_allowlist_then_column_rule_applied_to_survivors(self):
        """Columns that survive the allowlist still get column rules applied."""
        p = make_policy(
            allowlist={"enabled": True, "assets": {"S.T": ["EMAIL"]}},
            rules=[{"space": "*", "columns": {"EMAIL": "redact"}}],
        )
        result, masked = apply_masking(ROWS, "S", "T", p)
        assert all(row["EMAIL"] == "***" for row in result)
        assert "EMAIL" in masked

    # ── value patterns ───────────────────────────────────────────────────────

    def test_value_pattern_triggers_default_action(self):
        rows = [{"NOTES": "Contact alice@example.com for details"}]
        p = make_policy(
            default_action="redact",
            patterns={"email": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"},
        )
        result, masked = apply_masking(rows, "S", "T", p)
        assert result[0]["NOTES"] == "***"
        assert "NOTES" in masked

    def test_value_pattern_not_applied_to_non_string(self):
        rows = [{"AMOUNT": 12345}]
        p = make_policy(
            default_action="redact",
            patterns={"digits": r"\d+"},
        )
        result, masked = apply_masking(rows, "S", "T", p)
        # Non-string values are not scanned by value patterns
        assert result[0]["AMOUNT"] == 12345
        assert masked == []

    # ── masked_fields list ───────────────────────────────────────────────────

    def test_masked_fields_sorted(self):
        p = make_policy(rules=[{"space": "*", "columns": {"EMAIL": "redact", "NAME": "hash"}}])
        _, masked = apply_masking(ROWS, "S", "T", p)
        assert masked == sorted(masked)

    # ── precedence: column rule beats value pattern ──────────────────────────

    def test_column_rule_takes_precedence_over_value_pattern(self):
        rows = [{"EMAIL": "alice@example.com"}]
        p = make_policy(
            default_action="redact",
            rules=[{"space": "*", "columns": {"EMAIL": "hash"}}],
            patterns={"email": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"},
        )
        result, _ = apply_masking(rows, "S", "T", p)
        # Should be a 64-char hex (hash), not "***" (redact)
        assert len(result[0]["EMAIL"]) == 64


# ─────────────────────────────────────────────────────────────────────────────
# load_policy
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadPolicy:
    def test_no_env_var_returns_none(self, monkeypatch):
        monkeypatch.delenv("DATASPHERE_PII_POLICY", raising=False)
        assert load_policy() is None

    def test_valid_json_policy(self, monkeypatch, tmp_path):
        import json as _json
        policy_file = tmp_path / "policy.json"
        policy_file.write_text(_json.dumps(MINIMAL_CFG))
        monkeypatch.setenv("DATASPHERE_PII_POLICY", str(policy_file))
        monkeypatch.setenv("DATASPHERE_PII_SALT", "salt")
        p = load_policy()
        assert p is not None
        assert p.mode == "enforce"

    def test_valid_yaml_policy(self, monkeypatch, tmp_path):
        pytest.importorskip("yaml")
        policy_file = tmp_path / "policy.yaml"
        policy_file.write_text(textwrap.dedent("""\
            mode: enforce
            default_action: redact
        """))
        monkeypatch.setenv("DATASPHERE_PII_POLICY", str(policy_file))
        monkeypatch.setenv("DATASPHERE_PII_SALT", "salt")
        p = load_policy()
        assert p is not None
        assert p.mode == "enforce"

    def test_missing_file_raises(self, monkeypatch):
        monkeypatch.setenv("DATASPHERE_PII_POLICY", "/nonexistent/policy.yaml")
        with pytest.raises(RuntimeError, match="Cannot open policy file"):
            load_policy()

    def test_unparseable_json_raises(self, monkeypatch, tmp_path):
        policy_file = tmp_path / "bad.json"
        policy_file.write_text("{ this is not valid json }")
        monkeypatch.setenv("DATASPHERE_PII_POLICY", str(policy_file))
        with pytest.raises(RuntimeError, match="not valid YAML/JSON"):
            load_policy()

    def test_non_dict_yaml_raises(self, monkeypatch, tmp_path):
        pytest.importorskip("yaml")
        policy_file = tmp_path / "list.yaml"
        policy_file.write_text("- item1\n- item2\n")
        monkeypatch.setenv("DATASPHERE_PII_POLICY", str(policy_file))
        with pytest.raises(RuntimeError, match="must contain a YAML/JSON object"):
            load_policy()

    def test_env_mode_overrides_file_mode(self, monkeypatch, tmp_path):
        import json as _json
        policy_file = tmp_path / "policy.json"
        policy_file.write_text(_json.dumps({**MINIMAL_CFG, "mode": "enforce"}))
        monkeypatch.setenv("DATASPHERE_PII_POLICY", str(policy_file))
        monkeypatch.setenv("DATASPHERE_PII_MODE", "audit_only")
        monkeypatch.setenv("DATASPHERE_PII_SALT", "salt")
        p = load_policy()
        assert p.mode == "audit_only"

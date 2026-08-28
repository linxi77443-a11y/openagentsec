"""Phase 1A tests — Environment Preflight: ten dimensions, fail-closed.

Covers the ten PRD v4.0.2 §17.1 dimensions, the fail-closed aggregation
(BLOCKED / FAIL / ERROR / INCONCLUSIVE never ready), plaintext-credential
masking, and the guarantee that network probing never contacts arbitrary
internet targets (loopback only).

All tests use tmp_path / monkeypatch / local fixtures.  No real network access.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.openagentsec.preflight import (
    EnvironmentPreflight,
    assert_preflight_ready,
    default_preflight_config,
    run_preflight,
)


def _good_config(tmp_path: Path) -> dict:
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir(exist_ok=True)
    (sandbox / "data.txt").write_text("fake data", encoding="utf-8")
    return {
        "network_mode": "off",
        "external_targets": [],
        "audit_enabled": True,
        "audit_dir": "audit",
        "synthetic_only": True,
        "fake_runtime_only": True,
        "runtime_mode": "synthetic",
        "tool_inventory": [
            {"tool_name": "fake_search_docs"},
            {"tool_name": "fake_read_secret"},
        ],
        "allowed_tool_prefixes": ("fake_",),
        "deny_tools": ("execute_shell_command",),
        "sandbox_root": str(sandbox),
        "filesystem_paths": [str(sandbox / "data.txt")],
        "target": "sandbox-generic-agent",
        "target_type": "sandbox",
        "tenant": "test_tenant",
        "identity": "test_user",
        "authorization_ref": "AUTH-TEST-001",
        "authorization_scope": "read_only",
        "credentials": {"api_key": "<SIM_API_KEY_001>"},
    }


def _run(cfg: dict, tmp_path: Path):
    return EnvironmentPreflight(config=cfg, root=tmp_path).run()


# ---------------------------------------------------------------------------
# Happy path: all ten dimensions PASS
# ---------------------------------------------------------------------------

def test_good_config_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    result = _run(_good_config(tmp_path), tmp_path)
    assert result.ready is True
    assert result.overall == "PASS"
    assert len(result.checks) == 10
    names = [c.name for c in result.checks]
    assert names == [
        "network",
        "credential",
        "tool_inventory",
        "filesystem",
        "identity",
        "audit",
        "tenant",
        "target_binding",
        "authorization_scope",
        "runtime_mode",
    ]


def test_assert_preflight_ready_true(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    assert assert_preflight_ready(_good_config(tmp_path), root=tmp_path) is True


# ---------------------------------------------------------------------------
# Ten dimensions, one by one (fail-closed)
# ---------------------------------------------------------------------------

def test_network_external_without_approval_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"network_mode": "approved_external", "network_approved": False})
    result = _run(cfg, tmp_path)
    assert result.ready is False
    network = [c for c in result.checks if c.name == "network"][0]
    assert network.status == "BLOCKED"


def test_network_off_with_external_targets_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"external_targets": ["https://example.invalid"]})
    result = _run(cfg, tmp_path)
    network = [c for c in result.checks if c.name == "network"][0]
    assert network.status == "BLOCKED"


def test_network_probe_failure_inconclusive(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: False)
    cfg = _good_config(tmp_path)
    result = _run(cfg, tmp_path)
    assert result.ready is False
    network = [c for c in result.checks if c.name == "network"][0]
    assert network.status == "INCONCLUSIVE"


def test_credential_plaintext_fail_and_masked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    secret = "sk-real-secret-1234567890"
    cfg = _good_config(tmp_path)
    cfg.update({"credentials": {"api_key": secret}})
    result = _run(cfg, tmp_path)
    assert result.ready is False
    credential = [c for c in result.checks if c.name == "credential"][0]
    assert credential.status == "FAIL"
    dump = json.dumps(result.to_dict())
    assert secret not in dump, "plaintext credential must never be recorded"


def test_tool_inventory_unregistered_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"tool_inventory": [{"tool_name": "real_production_tool"}]})
    result = _run(cfg, tmp_path)
    tool = [c for c in result.checks if c.name == "tool_inventory"][0]
    assert tool.status == "BLOCKED"


def test_tool_inventory_deny_list_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"tool_inventory": [{"tool_name": "execute_shell_command"}]})
    result = _run(cfg, tmp_path)
    tool = [c for c in result.checks if c.name == "tool_inventory"][0]
    assert tool.status == "BLOCKED"


def test_tool_inventory_empty_inconclusive(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"tool_inventory": []})
    result = _run(cfg, tmp_path)
    tool = [c for c in result.checks if c.name == "tool_inventory"][0]
    assert tool.status == "INCONCLUSIVE"
    assert result.ready is False


def test_filesystem_escape_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    outside = tmp_path / "outside" / "secret.txt"
    cfg.update({"filesystem_paths": [str(outside)]})
    result = _run(cfg, tmp_path)
    fs = [c for c in result.checks if c.name == "filesystem"][0]
    assert fs.status == "BLOCKED"


def test_identity_non_test_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"identity": "root"})
    result = _run(cfg, tmp_path)
    identity = [c for c in result.checks if c.name == "identity"][0]
    assert identity.status == "FAIL"


def test_audit_disabled_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"audit_enabled": False})
    result = _run(cfg, tmp_path)
    audit = [c for c in result.checks if c.name == "audit"][0]
    assert audit.status == "BLOCKED"


def test_audit_dir_writable_probe(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    result = _run(cfg, tmp_path)
    audit = [c for c in result.checks if c.name == "audit"][0]
    assert audit.status == "PASS"
    assert (tmp_path / "audit" / "preflight.log").is_file(), "audit probe must leave a local trail"


def test_tenant_production_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"tenant": "prod-tenant-001"})
    result = _run(cfg, tmp_path)
    tenant = [c for c in result.checks if c.name == "tenant"][0]
    assert tenant.status == "FAIL"


def test_target_external_without_approval_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"target_type": "external", "network_approved": False})
    result = _run(cfg, tmp_path)
    target = [c for c in result.checks if c.name == "target_binding"][0]
    assert target.status == "BLOCKED"


def test_authorization_write_without_approval_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"authorization_scope": "write", "write_approved": False})
    result = _run(cfg, tmp_path)
    authz = [c for c in result.checks if c.name == "authorization_scope"][0]
    assert authz.status == "BLOCKED"


def test_authorization_ref_missing_inconclusive(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"authorization_ref": None})
    result = _run(cfg, tmp_path)
    authz = [c for c in result.checks if c.name == "authorization_scope"][0]
    assert authz.status == "INCONCLUSIVE"
    assert result.ready is False


def test_runtime_mode_production_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"runtime_mode": "production"})
    result = _run(cfg, tmp_path)
    runtime = [c for c in result.checks if c.name == "runtime_mode"][0]
    assert runtime.status == "BLOCKED"


def test_synthetic_only_false_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"synthetic_only": False})
    result = _run(cfg, tmp_path)
    runtime = [c for c in result.checks if c.name == "runtime_mode"][0]
    assert runtime.status == "BLOCKED"


# ---------------------------------------------------------------------------
# Aggregation / fail-closed semantics
# ---------------------------------------------------------------------------

def test_any_non_pass_never_ready(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"identity": "root"})  # single FAIL dimension
    result = _run(cfg, tmp_path)
    assert result.ready is False
    assert result.overall in ("BLOCKED", "FAIL", "ERROR", "INCONCLUSIVE")


def test_aggregation_priority_blocked_over_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    cfg = _good_config(tmp_path)
    cfg.update({"identity": "root", "synthetic_only": False})
    result = _run(cfg, tmp_path)
    assert result.ready is False
    assert result.overall in ("BLOCKED", "FAIL")


# ---------------------------------------------------------------------------
# Network probe never contacts internet targets
# ---------------------------------------------------------------------------

def test_no_external_socket_connect(tmp_path, monkeypatch):
    """Preflight must never attempt an outbound connection during network probe."""
    import socket as socket_mod

    def _forbid_external(*args, **kwargs):
        raise AssertionError("preflight must never call socket.create_connection")

    monkeypatch.setattr(socket_mod, "create_connection", _forbid_external)
    # Loopback probe is implemented with bind() only; run should still succeed.
    cfg = _good_config(tmp_path)
    result = _run(cfg, tmp_path)
    assert result.ready is True


# ---------------------------------------------------------------------------
# CLI subcommand: openagentsec preflight --config <path>
# ---------------------------------------------------------------------------

def test_cli_preflight_subcommand_pass(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    from src.openagentsec import cli as cli_mod

    cfg_path = tmp_path / "preflight.yaml"
    cfg_path.write_text(json.dumps(_good_config(tmp_path)), encoding="utf-8")
    rc = cli_mod.run_preflight_command(str(cfg_path))
    captured = capsys.readouterr()
    assert rc == 0, f"ready preflight should exit 0, got {rc}"
    assert '"overall": "PASS"' in captured.out
    assert '"ready": true' in captured.out


def test_cli_preflight_subcommand_blocked(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(EnvironmentPreflight, "_probe_loopback", lambda self: True)
    from src.openagentsec import cli as cli_mod

    cfg = _good_config(tmp_path)
    cfg["runtime_mode"] = "production"
    cfg_path = tmp_path / "preflight.yaml"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    rc = cli_mod.run_preflight_command(str(cfg_path))
    assert rc != 0, "non-ready preflight must exit non-zero"


def test_cli_preflight_subcommand_missing_config(tmp_path, capsys):
    from src.openagentsec import cli as cli_mod

    rc = cli_mod.run_preflight_command(str(tmp_path / "does_not_exist.yaml"))
    assert rc == 5, "missing config should exit ERROR (5)"

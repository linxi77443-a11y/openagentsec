"""Tests for CLI result authenticity (PRD P0-06 / v3.2 §7.3).

Covers: NOT_FOUND, BLOCKED, INCONCLUSIVE, ERROR, PASS, FAIL, evidence/hash
integrity, and audit fail-closed scenarios.  All scenarios use tmp_path fixtures
and never touch the real executions/ directory.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]

from src.openagentsec.cli import (
    main,
    eval_module,
    audit_summary,
    EXIT_PASS,
    EXIT_NOT_FOUND,
    EXIT_FAIL,
    EXIT_BLOCKED,
    EXIT_INCONCLUSIVE,
    EXIT_ERROR,
)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_registry(tmp_path: Path, module_ids=("M01",)) -> Path:
    p = tmp_path / "capability_modules" / "module_registry.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "modules": [
            {
                "module_id": m,
                "module_name": f"Module {m}",
                "priority": "P0",
                "layer": "test",
                "coverage": {"coverage_status": "mvp_complete"},
            }
            for m in module_ids
        ]
    }
    p.write_text(yaml.dump(data), encoding="utf-8")
    return p


def _write_trusted_result(
    exec_dir: Path,
    module_id: str = "M01",
    final_status: str = "PASS",
    assessment_mode: str = "adversarial_validation",
    evidence_refs=("ev-001",),
) -> Path:
    """Write a fully trusted result (evidence files + valid SHA-256 hash)."""
    exec_dir.mkdir(parents=True, exist_ok=True)
    for ref in evidence_refs:
        (exec_dir / str(ref)).write_text(f"evidence payload for {ref}", encoding="utf-8")
    trace_path = exec_dir / "trace.json"
    trace_path.write_text('{"trace": []}', encoding="utf-8")
    artifact_hashes = {"trace.json": _hash_file(trace_path)}
    for ref in evidence_refs:
        artifact_hashes[str(ref)] = _hash_file(exec_dir / str(ref))

    body = {
        "module_id": module_id,
        "run_id": "run-001",
        "assessment_mode": assessment_mode,
        "maturity_level": "L3",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": list(evidence_refs),
        "artifact_hashes": artifact_hashes,
        "final_status": final_status,
        "total_cases": 10,
        "breakthrough_detected_count": 0,
        "synthetic_only": True,
    }
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    return result_path


@pytest.fixture
def scratch_registry(tmp_path):
    """Minimal registry with a single known module M01."""
    _make_registry(tmp_path)
    return tmp_path


@pytest.fixture
def scratch_registry_and_exec(tmp_path):
    """Registry + fully trusted PASS execution result for M01."""
    _make_registry(tmp_path)
    _write_trusted_result(tmp_path / "executions" / "phase01_m01_test")
    return tmp_path


def _patch_root(tmp_path):
    """Temporarily redirect CLI ROOT to *tmp_path*."""
    import src.openagentsec.cli as cli_mod
    old = cli_mod.ROOT
    cli_mod.ROOT = tmp_path
    return old


def _restore_root(old):
    import src.openagentsec.cli as cli_mod
    cli_mod.ROOT = old


# ---------------------------------------------------------------------------
# NOT_FOUND: M999 (non-existent module)
# ---------------------------------------------------------------------------

def test_m999_not_found(scratch_registry):
    root = scratch_registry
    old = _patch_root(root)
    try:
        rc = main(["eval", "-t", "M999"])
        assert rc == EXIT_NOT_FOUND, f"expected NOT_FOUND (1), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# NOT_FOUND: module exists but no execution results
# ---------------------------------------------------------------------------

def test_module_exists_no_results(scratch_registry):
    root = scratch_registry
    old = _patch_root(root)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_NOT_FOUND, f"no results should be NOT_FOUND (1), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# INCONCLUSIVE: multiple candidate results -> ambiguous
# ---------------------------------------------------------------------------

def test_multiple_candidates_inconclusive(tmp_path, capsys):
    _make_registry(tmp_path)
    _write_trusted_result(tmp_path / "executions" / "phase01_m01_a")
    _write_trusted_result(tmp_path / "executions" / "phase01_m01_b")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_INCONCLUSIVE, f"ambiguous results should be INCONCLUSIVE (4), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "AMBIGUOUS_RESULT_SET" in captured.out


# ---------------------------------------------------------------------------
# ERROR: result file empty
# ---------------------------------------------------------------------------

def test_empty_result_file(scratch_registry_and_exec):
    root = scratch_registry_and_exec
    old = _patch_root(root)
    (root / "executions" / "phase01_m01_test" / "result.yaml").write_text("", encoding="utf-8")
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"empty result should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# ERROR: result file is invalid YAML
# ---------------------------------------------------------------------------

def test_corrupt_result_yaml(scratch_registry_and_exec):
    root = scratch_registry_and_exec
    old = _patch_root(root)
    (root / "executions" / "phase01_m01_test" / "result.yaml").write_text("{broken: [", encoding="utf-8")
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"corrupt yaml should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# ERROR: result module_id does not match queried target
# ---------------------------------------------------------------------------

def test_module_id_mismatch(tmp_path, capsys):
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    (exec_dir / "ev-001").write_text("evidence", encoding="utf-8")
    body = {
        "module_id": "M02",
        "run_id": "run-001",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": {},
        "final_status": "PASS",
    }
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    body["artifact_hashes"]["result.yaml"] = _hash_file(result_path)
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"module_id mismatch should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "MODULE_ID_MISMATCH" in captured.out


# ---------------------------------------------------------------------------
# INCONCLUSIVE: contract fields missing/empty but file parses
# ---------------------------------------------------------------------------

def test_incomplete_contract_inconclusive(tmp_path, capsys):
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    (exec_dir / "result.yaml").write_text(
        yaml.dump({"module_id": "M01", "final_status": "PASS"}), encoding="utf-8"
    )
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_INCONCLUSIVE, f"incomplete contract should be INCONCLUSIVE (4), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "INCOMPLETE_RESULT_CONTRACT" in captured.out


def test_legacy_verdict_inconclusive(tmp_path, capsys):
    """evaluation_verdict: PASS alone must never auto-upgrade to trusted PASS."""
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    (exec_dir / "result.yaml").write_text(
        yaml.dump({"module_id": "M01", "evaluation_verdict": "PASS"}), encoding="utf-8"
    )
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_INCONCLUSIVE, f"legacy verdict should be INCONCLUSIVE (4), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "UNTRUSTED_LEGACY_RESULT" in captured.out


# ---------------------------------------------------------------------------
# ERROR: evidence ref missing
# ---------------------------------------------------------------------------

def test_evidence_ref_missing(tmp_path):
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    body = {
        "module_id": "M01",
        "run_id": "run-001",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": {},
        "final_status": "PASS",
    }
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    body["artifact_hashes"]["result.yaml"] = _hash_file(result_path)
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"missing evidence should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# ERROR: evidence path escapes allowed scope
# ---------------------------------------------------------------------------

def test_evidence_path_escape(tmp_path, capsys):
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    (exec_dir / "ev-001").write_text("evidence", encoding="utf-8")
    body = {
        "module_id": "M01",
        "run_id": "run-001",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["../escape.txt"],
        "artifact_hashes": {},
        "final_status": "PASS",
    }
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    body["artifact_hashes"]["result.yaml"] = _hash_file(result_path)
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"path escape should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "PATH_ESCAPE" in captured.out


# ---------------------------------------------------------------------------
# ERROR: artifact hash format invalid
# ---------------------------------------------------------------------------

def test_artifact_hash_invalid_format(tmp_path):
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    (exec_dir / "ev-001").write_text("evidence", encoding="utf-8")
    body = {
        "module_id": "M01",
        "run_id": "run-001",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": {"ev-001": _hash_file(exec_dir / "ev-001"), "result.yaml": "abc123"},
        "final_status": "PASS",
    }
    (exec_dir / "result.yaml").write_text(yaml.dump(body), encoding="utf-8")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"invalid hash format should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# ERROR: artifact SHA-256 mismatch
# ---------------------------------------------------------------------------

def test_artifact_hash_mismatch(tmp_path, capsys):
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    (exec_dir / "ev-001").write_text("evidence", encoding="utf-8")
    body = {
        "module_id": "M01",
        "run_id": "run-001",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": {"ev-001": _hash_file(exec_dir / "ev-001"), "result.yaml": "0" * 64},
        "final_status": "PASS",
    }
    (exec_dir / "result.yaml").write_text(yaml.dump(body), encoding="utf-8")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_ERROR, f"hash mismatch should be ERROR (5), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "HASH_MISMATCH" in captured.out


# ---------------------------------------------------------------------------
# Normal trusted PASS
# ---------------------------------------------------------------------------

def test_normal_pass(scratch_registry_and_exec, capsys):
    old = _patch_root(scratch_registry_and_exec)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_PASS, f"valid trusted result should be PASS (0), got {rc}"
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "[PASS] Module: M01" in captured.out
    assert "run_id" in captured.out
    assert "artifact_hashes" in captured.out


# ---------------------------------------------------------------------------
# Trusted FAIL status
# ---------------------------------------------------------------------------

def test_fail_status(tmp_path):
    _make_registry(tmp_path)
    _write_trusted_result(tmp_path / "executions" / "phase01_m01_test", final_status="FAIL")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_FAIL, f"trusted FAIL should be EXIT_FAIL (2), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# BLOCKED status passthrough
# ---------------------------------------------------------------------------

def test_blocked_status(scratch_registry_and_exec):
    root = scratch_registry_and_exec
    old = _patch_root(root)
    (root / "executions" / "phase01_m01_test" / "result.yaml").write_text(
        yaml.dump({"final_status": "BLOCKED", "run_id": "run-001", "module_id": "M01"}),
        encoding="utf-8",
    )
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_BLOCKED, f"BLOCKED should be EXIT_BLOCKED (3), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# INCONCLUSIVE status passthrough
# ---------------------------------------------------------------------------

def test_inconclusive_status(scratch_registry_and_exec):
    root = scratch_registry_and_exec
    old = _patch_root(root)
    (root / "executions" / "phase01_m01_test" / "result.yaml").write_text(
        yaml.dump({"final_status": "INCONCLUSIVE", "run_id": "run-001", "module_id": "M01"}),
        encoding="utf-8",
    )
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_INCONCLUSIVE, f"INCONCLUSIVE should be EXIT_INCONCLUSIVE (4), got {rc}"
    finally:
        _restore_root(old)


# ---------------------------------------------------------------------------
# assessment_mode / synthetic_only come from the result, not hardcoded
# ---------------------------------------------------------------------------

def test_assessment_mode_comes_from_result(tmp_path, capsys):
    _make_registry(tmp_path)
    _write_trusted_result(
        tmp_path / "executions" / "phase01_m01_test",
        assessment_mode="defensive_evaluation",
    )
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_PASS
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "defensive_evaluation" in captured.out
    assert "synthetic_only:      true" in captured.out


def test_unknown_fields_not_hardcoded(tmp_path, capsys):
    """Missing assessment_mode/synthetic_only must not be fabricated."""
    _make_registry(tmp_path)
    exec_dir = tmp_path / "executions" / "phase01_m01_test"
    exec_dir.mkdir(parents=True)
    ev_path = exec_dir / "ev-001"
    ev_path.write_text("evidence", encoding="utf-8")
    body = {
        "module_id": "M01",
        "run_id": "run-001",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": {"ev-001": _hash_file(ev_path)},
        "final_status": "PASS",
    }
    (exec_dir / "result.yaml").write_text(yaml.dump(body), encoding="utf-8")
    old = _patch_root(tmp_path)
    try:
        rc = main(["eval", "-t", "M01"])
        assert rc == EXIT_PASS
    finally:
        _restore_root(old)
    captured = capsys.readouterr()
    assert "assessment_mode:" not in captured.out
    assert "synthetic_only:      unknown" in captured.out


# ---------------------------------------------------------------------------
# audit: no trusted results -> INCONCLUSIVE, exit 4, no certified text
# ---------------------------------------------------------------------------

def test_audit_no_trusted_result_inconclusive(scratch_registry):
    root = scratch_registry
    old = _patch_root(root)
    try:
        rc = main(["audit", "--report", "json"])
        assert rc == EXIT_INCONCLUSIVE, f"audit without trusted results should be INCONCLUSIVE (4), got {rc}"
    finally:
        _restore_root(old)


def test_audit_no_hardcoded_certified():
    """audit must not contain hardcoded certified/released/verified verdicts."""
    output = audit_summary(output_format="json")
    data = json.loads(output)
    assert "verdict" in data
    assert data["verdict"] != "VERDICT_MILESTONE_6_0_PASSED_CERTIFIED", (
        "audit must not contain hardcoded certified verdict"
    )
    for banned in ("certified", "released", "verified"):
        assert banned not in output.lower(), f"audit must not contain '{banned}'"
    assert "overall_status" in data
    assert data["verdict"] == "implementation_in_progress"


def test_audit_text_no_pass():
    """Text audit output must not claim certified or 100% passed."""
    output = audit_summary(output_format="text")
    assert "certified" not in output.lower(), "text audit must not claim certified"
    assert "released" not in output.lower(), "text audit must not claim released"
    assert "100% passed" not in output.lower(), "text audit must not claim 100% passed"


# ---------------------------------------------------------------------------
# static validation_passed ≠ security_passed
# ---------------------------------------------------------------------------

def test_static_validation_not_security_passed():
    """Static schema validation alone must not claim security_passed."""
    import inspect
    import src.openagentsec.cli as cli_mod
    src = inspect.getsource(cli_mod)
    assert "security_passed" not in src, (
        "CLI must not contain 'security_passed' — static validation "
        "does not imply security_passed"
    )


# ---------------------------------------------------------------------------
# Known-good: real M48 evaluation (integration smoke test)
# ---------------------------------------------------------------------------

def test_real_m48_eval():
    """M48 must never be a trusted PASS while its real results are legacy/ambiguous."""
    old = _patch_root(ROOT)
    try:
        rc = eval_module("M48")
        assert rc != EXIT_PASS, (
            "M48 must not return PASS: its current real results are old, incomplete "
            "or ambiguous (multiple candidate result files without run selection)"
        )
        assert rc in (EXIT_PASS, EXIT_FAIL, EXIT_BLOCKED, EXIT_INCONCLUSIVE, EXIT_ERROR, EXIT_NOT_FOUND), (
            f"unexpected exit code for M48: {rc}"
        )
    finally:
        _restore_root(old)

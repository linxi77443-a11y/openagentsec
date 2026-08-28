"""Phase 1A tests — Result Integrity: canonical vs legacy status handling.

Verifies that legacy non-canonical status values (``closed/judge_approved``,
``*_VALIDATED``, ``VERDICT_*_CERTIFIED``, ``released``, ``certified``,
``verified``) are treated as *source metadata* only and are never upgraded to a
canonical PASS/FAIL.  Also verifies the three semantic axes
(``evaluation_status`` / ``artifact_status`` / ``legacy_source_status``) stay
separate, and that version metadata keeps ``product_prd_version`` distinct from
``software_version``.

All scenarios use tmp_path fixtures and never touch the real executions/ dir.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from src.openagentsec import cli as cli_mod
from src.openagentsec.cli import (
    EXIT_ERROR,
    EXIT_FAIL,
    EXIT_INCONCLUSIVE,
    EXIT_PASS,
    main,
)
from src.openagentsec.result_contract import (
    REASON_LEGACY_NONCANONICAL_RESULT,
    REASON_UNTRUSTED_LEGACY_RESULT,
    is_legacy_source_status,
    resolve_legacy_status,
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


def _write_trusted_result(exec_dir: Path, module_id: str = "M01", final_status: str = "PASS") -> Path:
    """Write a fully trusted canonical result (evidence files + valid hashes)."""
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "ev-001").write_text("evidence payload", encoding="utf-8")
    trace_path = exec_dir / "trace.json"
    trace_path.write_text('{"trace": []}', encoding="utf-8")
    artifact_hashes = {
        "trace.json": _hash_file(trace_path),
        "ev-001": _hash_file(exec_dir / "ev-001"),
    }
    body = {
        "module_id": module_id,
        "run_id": "run-001",
        "assessment_mode": "adversarial_validation",
        "maturity_level": "L3",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": artifact_hashes,
        "final_status": final_status,
        "synthetic_only": True,
    }
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    return result_path


def _write_raw_result(exec_dir: Path, body: dict) -> Path:
    exec_dir.mkdir(parents=True, exist_ok=True)
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    return result_path


def _patch_root(tmp_path: Path):
    old = cli_mod.ROOT
    cli_mod.ROOT = tmp_path
    return old


def _restore_root(old):
    cli_mod.ROOT = old


@pytest.fixture
def scratch(tmp_path):
    _make_registry(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# is_legacy_source_status / resolve_legacy_status unit checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [
        ("closed/judge_approved", True),
        ("CLOSED", True),
        ("M36_SIDECHANNEL_TIMING_EVALUATOR_VALIDATED", True),
        ("VERDICT_MILESTONE_6_0_PASSED_CERTIFIED", True),
        ("released", True),
        ("certified", True),
        ("verified", True),
        ("PASS", False),
        ("FAIL", False),
        ("INCONCLUSIVE", False),
        ("BLOCKED", False),
        ("ERROR", False),
        ("NOT_FOUND", False),
        ("", False),
        (123, False),
        (None, False),
    ],
)
def test_is_legacy_source_status(value, expected):
    assert is_legacy_source_status(value) is expected


def test_resolve_legacy_status_finds_first_legacy():
    data = {"module_id": "M01", "status": "closed/judge_approved", "final_status": "released"}
    assert resolve_legacy_status(data) in ("closed/judge_approved", "released")


def test_resolve_legacy_status_none_for_canonical():
    assert resolve_legacy_status({"final_status": "PASS"}) is None
    assert resolve_legacy_status({"evaluation_verdict": "PASS"}) is None


# ---------------------------------------------------------------------------
# CLI-level: legacy-only results -> INCONCLUSIVE + LEGACY_NONCANONICAL_RESULT
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "status_field,status_value",
    [
        ("status", "closed/judge_approved"),
        ("final_status", "M36_TIMING_EVALUATOR_VALIDATED"),
        ("status", "VERDICT_MILESTONE_6_0_PASSED_CERTIFIED"),
        ("status", "released"),
        ("status", "certified"),
        ("status", "verified"),
    ],
)
def test_legacy_only_inconclusive(scratch, capsys, status_field, status_value):
    """A result carrying only a legacy non-canonical status must be INCONCLUSIVE."""
    _write_raw_result(
        scratch / "executions" / "phase01_m01_test",
        {"module_id": "M01", status_field: status_value},
    )
    old = _patch_root(scratch)
    try:
        rc = main(["eval", "-t", "M01"])
    finally:
        _restore_root(old)
    assert rc == EXIT_INCONCLUSIVE, f"legacy-only status must be INCONCLUSIVE (4), got {rc}"
    captured = capsys.readouterr()
    assert "LEGACY_NONCANONICAL_RESULT" in captured.out
    assert "not mapped to PASS/FAIL" in captured.out


def test_legacy_only_never_maps_to_pass(scratch):
    """Even a legacy value containing 'verified'/'certified' must not yield PASS."""
    _write_raw_result(
        scratch / "executions" / "phase01_m01_test",
        {"module_id": "M01", "status": "verified"},
    )
    old = _patch_root(scratch)
    try:
        rc = main(["eval", "-t", "M01"])
    finally:
        _restore_root(old)
    assert rc != EXIT_PASS


# ---------------------------------------------------------------------------
# Canonical present -> canonical wins; legacy retained only as source metadata
# ---------------------------------------------------------------------------

def test_canonical_wins_over_legacy(scratch):
    """Canonical final_status=PASS with a legacy 'closed' field stays PASS."""
    _write_trusted_result(
        scratch / "executions" / "phase01_m01_test",
        final_status="PASS",
    )
    result_path = scratch / "executions" / "phase01_m01_test" / "result.yaml"
    data = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    data["status"] = "closed/judge_approved"
    result_path.write_text(yaml.dump(data), encoding="utf-8")
    old = _patch_root(scratch)
    try:
        rc = main(["eval", "-t", "M01"])
    finally:
        _restore_root(old)
    assert rc == EXIT_PASS, f"canonical PASS must win over legacy field, got {rc}"


def test_evaluation_verdict_pass_still_untrusted(scratch, capsys):
    """Legacy evaluation_verdict: PASS alone must never auto-upgrade to PASS."""
    _write_raw_result(
        scratch / "executions" / "phase01_m01_test",
        {"module_id": "M01", "evaluation_verdict": "PASS"},
    )
    old = _patch_root(scratch)
    try:
        rc = main(["eval", "-t", "M01"])
    finally:
        _restore_root(old)
    assert rc == EXIT_INCONCLUSIVE
    captured = capsys.readouterr()
    assert "UNTRUSTED_LEGACY_RESULT" in captured.out


# ---------------------------------------------------------------------------
# Three semantic axes stay separate on the contract object
# ---------------------------------------------------------------------------

def _load_contract(scratch, body_or_path):
    if isinstance(body_or_path, dict):
        path = _write_raw_result(scratch / "executions" / "phase01_m01_test", body_or_path)
    else:
        path = body_or_path
    return cli_mod._load_single_result("M01", path)


def test_three_semantics_for_trusted_result(scratch):
    _write_trusted_result(scratch / "executions" / "phase01_m01_test", final_status="PASS")
    rc = _load_contract(scratch, scratch / "executions" / "phase01_m01_test" / "result.yaml")
    assert rc.evaluation_status == "PASS"
    assert rc.artifact_status == "verified"
    assert rc.legacy_source_status is None


def test_three_semantics_for_legacy_result(scratch):
    rc = _load_contract(
        scratch,
        {"module_id": "M01", "status": "closed/judge_approved"},
    )
    assert rc.status == "INCONCLUSIVE"
    assert rc.evaluation_status == "INCONCLUSIVE"
    assert rc.artifact_status == "unverified"
    assert rc.legacy_source_status == "closed/judge_approved"
    assert rc.reason_code == REASON_LEGACY_NONCANONICAL_RESULT


def test_three_semantics_for_incomplete_result(scratch):
    rc = _load_contract(scratch, {"module_id": "M01", "final_status": "PASS"})
    assert rc.evaluation_status == "PASS"
    assert rc.artifact_status == "incomplete"
    assert rc.legacy_source_status is None


def test_three_semantics_for_untrusted_verdict(scratch):
    rc = _load_contract(scratch, {"module_id": "M01", "evaluation_verdict": "PASS"})
    assert rc.status == "INCONCLUSIVE"
    assert rc.artifact_status == "unverified"
    assert rc.reason_code == REASON_UNTRUSTED_LEGACY_RESULT


# ---------------------------------------------------------------------------
# Version semantics: product_prd_version != software_version
# ---------------------------------------------------------------------------

def test_version_metadata_distinct(scratch):
    _write_trusted_result(scratch / "executions" / "phase01_m01_test", final_status="PASS")
    rc = _load_contract(scratch, scratch / "executions" / "phase01_m01_test" / "result.yaml")
    assert rc.product_prd_version == "4.0.2"
    assert rc.software_version == "6.0.0"
    assert rc.software_version != rc.product_prd_version, (
        "software_version must never be lowered to the PRD version"
    )

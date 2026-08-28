"""Phase 22.0C Reproduction Integrity Boundary tests."""

from __future__ import annotations

from copy import deepcopy
import hashlib

from src.openagentsec.oracle.enums import OracleDecision
from src.openagentsec.reproduction import (
    ReproductionAggregator,
    ReproductionIntegrityVerifier,
    ReproductionRun,
    ReproductionStatus,
)


BASELINE_HASH = "baseline-phase-22-0c"


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _make_run(
    index: int,
    decision: OracleDecision = OracleDecision.CONFIRMED_DEVIATION,
) -> ReproductionRun:
    evidence_id = f"EV-RUN-{index:03d}"
    is_deviation = decision == OracleDecision.CONFIRMED_DEVIATION
    run = ReproductionRun(
        run_id=f"RUN-{index:03d}",
        session_id=f"SESSION-{index:03d}",
        run_index=index,
        baseline_hash=BASELINE_HASH,
        oracle_decision=decision,
        violated_invariants=["INV-TOOL-ALLOWLIST-001"] if is_deviation else [],
        deviation_present=is_deviation,
        deviation_severity="critical" if is_deviation else None,
        reason_codes=["denied_tool_executed_at_runtime"] if is_deviation else [],
        evidence_refs=[evidence_id],
        evidence_hashes={evidence_id: _sha256(f"evidence-content-{index}")},
        execution_receipt_ids=[f"EXEC-{index:03d}"],
        normalized_findings=(
            [
                {
                    "finding_type": "denied_tool_execution",
                    "tool": "export_internal_docs",
                    "timestamp": f"2026-08-23T00:00:0{index}Z",
                    "run_id": f"RUN-{index:03d}",
                }
            ]
            if is_deviation
            else []
        ),
    )
    _seal(run)
    return run


def _seal(run: ReproductionRun) -> None:
    run.evidence_instance_digest = (
        ReproductionIntegrityVerifier.compute_evidence_instance_digest(run)
    )
    run.evidence_outcome_digest = (
        ReproductionIntegrityVerifier.compute_evidence_outcome_digest(run)
    )


def _five_runs() -> list[ReproductionRun]:
    return [_make_run(index) for index in range(1, 6)]


def test_unique_run_id_validation_rejects_duplicate() -> None:
    runs = _five_runs()
    runs[1].run_id = runs[0].run_id
    _seal(runs[1])

    result = ReproductionAggregator.aggregate(runs)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.integrity_verified is False
    assert "duplicate_run_id" in result.reason_codes


def test_unique_session_validation_rejects_reuse() -> None:
    runs = _five_runs()
    runs[1].session_id = runs[0].session_id
    _seal(runs[1])

    result = ReproductionAggregator.aggregate(runs)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert "duplicate_session_id" in result.reason_codes


def test_duplicate_evidence_instance_digest_is_rejected() -> None:
    runs = _five_runs()
    runs[1].evidence_instance_digest = runs[0].evidence_instance_digest

    result = ReproductionAggregator.aggregate(runs)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert "duplicate_evidence_instance_digest" in result.reason_codes


def test_same_normalized_outcome_digest_reproduces_successfully() -> None:
    runs = _five_runs()

    result = ReproductionAggregator.aggregate(runs)

    assert len({run.evidence_instance_digest for run in runs}) == 5
    assert len({run.evidence_outcome_digest for run in runs}) == 1
    assert result.reproduction_status == ReproductionStatus.REPRODUCED
    assert result.integrity_verified is True
    assert result.is_reproduced_deviation is True
    assert result.evidence_outcome_digest == runs[0].evidence_outcome_digest
    assert "reproduction_integrity_verified" in result.reason_codes


def test_different_outcome_digest_is_rejected_without_majority_vote() -> None:
    runs = _five_runs()
    runs[4] = _make_run(5, OracleDecision.NO_CONFIRMED_DEVIATION)

    result = ReproductionAggregator.aggregate(runs)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.reproduced_outcome is None
    assert result.is_reproduced_deviation is False
    assert "evidence_outcome_digest_variance" in result.reason_codes


def test_copied_single_run_artifact_is_rejected_after_relabeling() -> None:
    original = _make_run(1)
    runs = [deepcopy(original) for _ in range(5)]
    for index, run in enumerate(runs, start=1):
        run.run_id = f"FORGED-RUN-{index:03d}"
        run.session_id = f"FORGED-SESSION-{index:03d}"
        run.run_index = index
        _seal(run)

    assert len({run.evidence_instance_digest for run in runs}) == 5
    result = ReproductionAggregator.aggregate(runs)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.integrity_verified is False
    assert "reused_evidence_id" in result.reason_codes
    assert "reused_execution_receipt_id" in result.reason_codes


def test_strict_integrity_requires_exactly_five_runs() -> None:
    result = ReproductionAggregator.aggregate(_five_runs()[:4])

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert "reproduction_run_count_invalid" in result.reason_codes


def test_run_indexes_must_be_continuous_one_through_five() -> None:
    runs = _five_runs()
    runs[4].run_index = 6
    _seal(runs[4])

    result = ReproductionAggregator.aggregate(runs)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert "invalid_run_index_sequence" in result.reason_codes


def test_malformed_identity_material_fails_closed() -> None:
    runs = _five_runs()
    runs[0].evidence_refs = [{"not": "an-id"}]  # type: ignore[list-item]
    runs[0].execution_receipt_ids = [{"not": "a-receipt"}]  # type: ignore[list-item]

    result = ReproductionAggregator.aggregate(runs, require_integrity=True)

    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.integrity_verified is False
    assert "invalid_evidence_id" in result.reason_codes
    assert "invalid_execution_receipt_ids" in result.reason_codes

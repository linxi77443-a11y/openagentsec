"""Shared Phase 22.1 strict Trust Chain helpers for existing runtimes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

from src.openagentsec.adapters.observation import ObservationResult
from src.openagentsec.oracle import (
    DeterministicToolBoundaryOracle,
    EvidenceEnvelope,
    EvidenceItem,
    EvidenceVerifier,
    ExecutionReceipt,
    ExecutionReceiptValidator,
    OracleResult,
)
from src.openagentsec.reproduction import (
    ReproductionIntegrityVerifier,
    ReproductionRun,
)


@dataclass(frozen=True)
class StrictEvaluation:
    """Artifacts produced by one complete strict Trust Chain evaluation."""

    envelopes: List[EvidenceEnvelope]
    receipts: List[ExecutionReceipt]
    oracle_result: OracleResult

    @property
    def evidence_hashes(self) -> Dict[str, str]:
        hashes: Dict[str, str] = {}
        for envelope in self.envelopes:
            content_hash = envelope.verification_result.content_hash
            if content_hash is None:
                raise AssertionError("verified Evidence must have a content hash")
            hashes[envelope.evidence_item.evidence_id] = content_hash
        return hashes


def evaluate_strict(
    *,
    oracle: DeterministicToolBoundaryOracle,
    policy: Any,
    objective: Any,
    observations: Dict[str, ObservationResult],
    evidence_items: Sequence[EvidenceItem],
) -> StrictEvaluation:
    """Run Evidence verification, receipt validation, and trusted Oracle entry."""
    verifier = EvidenceVerifier()
    envelopes = [verifier.verify(item) for item in evidence_items]
    invalid = [
        envelope.evidence_item.evidence_id
        for envelope in envelopes
        if not verifier.is_trusted(envelope)
    ]
    if invalid:
        raise AssertionError(f"strict Evidence verification failed: {invalid}")

    trusted_items = verifier.trusted_evidence_items(envelopes)
    receipt_validator = ExecutionReceiptValidator()
    receipts = receipt_validator.receipts_from_evidence(trusted_items)
    result = oracle.evaluate_verified(
        policy=policy,
        objective=objective,
        observations=observations,
        evidence_envelopes=envelopes,
        verifier=verifier,
        receipt_validator=receipt_validator,
    )
    return StrictEvaluation(
        envelopes=envelopes,
        receipts=receipts,
        oracle_result=result,
    )


def build_integrity_run(
    *,
    strict_evaluation: StrictEvaluation,
    run_id: str,
    session_id: str,
    run_index: int,
    baseline_hash: str,
    normalized_findings: Iterable[Dict[str, Any]],
) -> ReproductionRun:
    """Bind a strict evaluation to one independently digestible run instance."""
    result = strict_evaluation.oracle_result
    run = ReproductionRun(
        run_id=run_id,
        session_id=session_id,
        run_index=run_index,
        baseline_hash=baseline_hash,
        oracle_decision=result.decision,
        violated_invariants=list(result.violated_invariants),
        deviation_present=result.deviation is not None,
        deviation_severity=(
            result.deviation.severity.value if result.deviation else None
        ),
        reason_codes=list(result.reason_codes),
        evidence_refs=[
            envelope.evidence_item.evidence_id
            for envelope in strict_evaluation.envelopes
        ],
        evidence_hashes=strict_evaluation.evidence_hashes,
        execution_receipt_ids=[
            receipt.execution_id for receipt in strict_evaluation.receipts
        ],
        normalized_findings=list(normalized_findings),
        reset_verified_before=True,
        reset_verified_after=True,
        valid=True,
    )
    run.evidence_instance_digest = (
        ReproductionIntegrityVerifier.compute_evidence_instance_digest(run)
    )
    run.evidence_outcome_digest = (
        ReproductionIntegrityVerifier.compute_evidence_outcome_digest(run)
    )
    return run


def strict_run_artifact(
    *,
    runtime: Dict[str, Any],
    run: ReproductionRun,
    stimulus: Dict[str, Any],
    observations: Dict[str, ObservationResult],
    strict_evaluation: StrictEvaluation,
    legacy_decision: str,
    integrity_verified: bool,
) -> Dict[str, Any]:
    """Serialize a redaction-safe strict run record for research artifacts."""
    return {
        "runtime": runtime,
        "run_id": run.run_id,
        "session_id": run.session_id,
        "stimulus": stimulus,
        "observations": [
            {"observation_id": name, **observation.to_dict()}
            for name, observation in sorted(observations.items())
        ],
        "verified_evidence": [
            envelope.to_dict() for envelope in strict_evaluation.envelopes
        ],
        "execution_receipts": [
            receipt.to_dict() for receipt in strict_evaluation.receipts
        ],
        "oracle_result": {
            **strict_evaluation.oracle_result.to_dict(),
            "legacy_decision": legacy_decision,
            "strict_decision": strict_evaluation.oracle_result.decision.value,
        },
        "reproduction": {
            "integrity_verified": integrity_verified,
            "instance_digest": run.evidence_instance_digest,
            "outcome_digest": run.evidence_outcome_digest,
        },
    }

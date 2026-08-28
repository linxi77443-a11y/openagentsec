"""Phase 22.0A Evidence trust-boundary integration tests."""

from __future__ import annotations

from pathlib import Path

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models import load_evaluation_objective, load_security_policy
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import (
    DeterministicToolBoundaryOracle,
    EvidenceItem,
    EvidenceVerifier,
    OracleDecision,
    VerificationStatus,
)


FIXTURE_ROOT = Path("tests/unit/fixtures/v4")


def _evidence(
    *,
    evidence_id: str = "EV-TRUST-001",
    evidence_type: str = "tool_execution_log",
    content=None,
    include_run_id: bool = True,
    producer_claim: bool = False,
) -> EvidenceItem:
    metadata = {
        "session_id": "SESSION-TRUST-001",
        "producer": "runtime_probe",
        "observation_id": "OBS-TRUST-001",
    }
    if include_run_id:
        metadata["run_id"] = "RUN-TRUST-001"
    return EvidenceItem(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        source="runtime.actual_execution",
        content=content if content is not None else {"tool": "query_public_kb"},
        verified=producer_claim,
        metadata=metadata,
    )


def _complete_observations(call_id: str | None = None):
    tool_record = {
        "tool": "export_internal_docs",
        "status": "completed",
        "verified_runtime_execution": True,
    }
    if call_id is not None:
        tool_record["call_id"] = call_id
    return {
        "actual_tool_execution": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=[tool_record],
            source="runtime.actual_execution",
        ),
        "tool_trace": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=[tool_record],
            source="runtime.tool_trace",
        ),
        "runtime_state": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value={"active_node": "tools_node"},
            source="runtime.state",
        ),
        "model_response": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value="completed",
            source="runtime.response",
        ),
    }


def test_missing_provenance_run_id_is_invalid() -> None:
    verifier = EvidenceVerifier()

    envelope = verifier.verify(_evidence(include_run_id=False))

    assert envelope.verification_result.status == VerificationStatus.INVALID
    assert envelope.verification_result.content_hash is None
    assert "run_id" in envelope.verification_result.reason
    assert envelope.is_trusted is False


def test_canonical_hash_is_consistent_and_content_sensitive() -> None:
    verifier = EvidenceVerifier()
    first = _evidence(content={"arguments": {"b": 2, "a": 1}, "tool": "read"})
    reordered = _evidence(content={"tool": "read", "arguments": {"a": 1, "b": 2}})
    changed = _evidence(content={"tool": "read", "arguments": {"a": 1, "b": 3}})

    first_result = verifier.verify(first).verification_result
    reordered_result = verifier.verify(reordered).verification_result
    changed_result = verifier.verify(changed).verification_result

    assert first_result.status == VerificationStatus.VALID
    assert first_result.content_hash == reordered_result.content_hash
    assert first_result.content_hash != changed_result.content_hash


def test_tampered_content_fails_reverification() -> None:
    verifier = EvidenceVerifier()
    evidence = _evidence(content={"tool": "read", "path": "README.md"})
    envelope = verifier.verify(evidence)
    assert envelope.is_trusted is True

    evidence.content["path"] = "secrets.txt"
    reverified = verifier.reverify(envelope)

    assert reverified.status == VerificationStatus.INVALID
    assert reverified.reason == "content_hash_mismatch"
    assert envelope.is_trusted is False


def test_tampered_provenance_fails_reverification() -> None:
    verifier = EvidenceVerifier()
    evidence = _evidence(content={"tool": "read", "path": "README.md"})
    envelope = verifier.verify(evidence)
    assert envelope.is_trusted is True

    evidence.metadata["session_id"] = "SESSION-ATTACKER-999"
    reverified = verifier.reverify(envelope)

    assert reverified.status == VerificationStatus.INVALID
    assert reverified.reason == "provenance_binding_mismatch"
    assert envelope.is_trusted is False


def test_producer_claim_without_verifier_result_is_not_trusted_evidence() -> None:
    verifier = EvidenceVerifier()
    producer_claim = _evidence(producer_claim=True)
    assert producer_claim.verified is True
    assert verifier.is_trusted(producer_claim) is False

    policy = load_security_policy(
        FIXTURE_ROOT / "security_policy" / "pol_mvp1_tool_boundary.yaml"
    )
    objective = load_evaluation_objective(
        FIXTURE_ROOT / "evaluation_objective" / "obj_mvp1_tool_selection.yaml"
    )
    result = DeterministicToolBoundaryOracle().evaluate_verified(
        policy,
        objective,
        _complete_observations(),
        evidence_envelopes=[producer_claim],
    )

    assert result.decision == OracleDecision.INCONCLUSIVE
    assert result.evidence_refs == []
    assert "execution_unverified_intent_only" in result.reason_codes


def test_valid_evidence_is_verified_and_eligible_for_oracle() -> None:
    verifier = EvidenceVerifier()
    tool_evidence = _evidence(
        evidence_id="EV-TRUST-TOOL-001",
        evidence_type="tool_execution_log",
        content={
            "receipt_type": "runtime_completion",
            "execution_receipt": {
                "execution_id": "EXEC-TRUST-001",
                "call_id": "CALL-TRUST-001",
                "tool_name": "export_internal_docs",
                "status": "completed",
                "producer": "runtime_probe",
                "run_id": "RUN-TRUST-001",
                "session_id": "SESSION-TRUST-001",
            },
        },
        producer_claim=False,
    )
    state_evidence = _evidence(
        evidence_id="EV-TRUST-STATE-001",
        evidence_type="state_transition_trace",
        content={"transitions": ["agent_node", "tools_node"]},
        producer_claim=False,
    )
    envelopes = [verifier.verify(tool_evidence), verifier.verify(state_evidence)]

    assert all(
        item.verification_result.status == VerificationStatus.VALID
        for item in envelopes
    )
    assert all(item.verification_result.content_hash for item in envelopes)
    assert all(item.is_trusted for item in envelopes)
    assert tool_evidence.verified is False

    policy = load_security_policy(
        FIXTURE_ROOT / "security_policy" / "pol_mvp1_tool_boundary.yaml"
    )
    objective = load_evaluation_objective(
        FIXTURE_ROOT / "evaluation_objective" / "obj_mvp1_tool_selection.yaml"
    )
    result = DeterministicToolBoundaryOracle().evaluate_verified(
        policy,
        objective,
        _complete_observations(call_id="CALL-TRUST-001"),
        evidence_envelopes=envelopes,
        verifier=verifier,
    )

    assert result.decision == OracleDecision.CONFIRMED_DEVIATION
    assert result.evidence_refs == ["EV-TRUST-TOOL-001", "EV-TRUST-STATE-001"]

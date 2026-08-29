"""Trusted ScenarioPlan execution on the existing Evidence / Oracle / Reproduction chain.

This is not a second evaluation framework. It only binds ScenarioRenderer output
to EvidenceVerifier, ExecutionReceiptValidator, evaluate_verified, and
integrity-gated ReproductionAggregator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from ..adapters.observation import ObservationResult, ObservationStatus
from ..models.enums import ObservabilityState
from ..models.evaluation_objective import EvaluationObjective
from ..models.security_policy import SecurityPolicy
from ..oracle import (
    DeterministicToolBoundaryOracle,
    EvidenceEnvelope,
    EvidenceItem,
    EvidenceVerifier,
    ExecutionReceipt,
    ExecutionReceiptValidator,
    OracleResult,
)
from ..planner.renderer import ScenarioRenderer
from ..planner.scenario import ScenarioPlan
from ..reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionIntegrityVerifier,
    ReproductionResult,
    ReproductionRun,
    compute_config_hash,
)


PRODUCER = "langgraph_mvp1.tools_node"


def json_safe(value: Any) -> Any:
    """Convert runtime objects into Evidence-canonical JSON."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    content = getattr(value, "content", None)
    if content is not None:
        return {"type": type(value).__name__, "content": json_safe(content)}
    return str(value)


@dataclass
class RuntimeCapture:
    """One runtime observation set. Producer claims are not trusted Evidence."""

    run_id: str
    session_id: str
    tool_executions: List[Dict[str, Any]]
    runtime_state: Any
    model_response: Any
    memory_state: Any = None
    audit_events: Any = None
    source: str = "langgraph_whitebox_instrumentation"
    producer: str = PRODUCER


@dataclass
class TrustedEvaluation:
    envelopes: List[EvidenceEnvelope]
    receipts: List[ExecutionReceipt]
    oracle_result: OracleResult
    observations: Dict[str, ObservationResult]
    evidence_items: List[EvidenceItem]

    @property
    def evidence_hashes(self) -> Dict[str, str]:
        hashes: Dict[str, str] = {}
        for envelope in self.envelopes:
            content_hash = envelope.verification_result.content_hash
            if content_hash:
                hashes[envelope.evidence_item.evidence_id] = content_hash
        return hashes


def attach_execution_receipts(
    executions: Sequence[Dict[str, Any]],
    *,
    run_id: str,
    session_id: str,
    producer: str,
) -> List[Dict[str, Any]]:
    """Annotate observed tool completions with ExecutionReceipt payloads."""
    annotated: List[Dict[str, Any]] = []
    for index, record in enumerate(executions or [], start=1):
        item = dict(record)
        tool_name = str(item.get("tool") or item.get("name") or "")
        call_id = str(item.get("call_id") or item.get("callId") or f"call-{index:02d}")
        status = str(item.get("status") or "completed")
        execution_id = str(item.get("execution_id") or f"exec-{run_id}-{index:02d}")
        receipt = {
            "execution_id": execution_id,
            "call_id": call_id,
            "tool_name": tool_name,
            "status": status,
            "producer": producer,
            "run_id": run_id,
            "session_id": session_id,
        }
        item.update(
            {
                "tool": tool_name,
                "call_id": call_id,
                "status": status,
                "execution_id": execution_id,
                "receipt_type": "tool_result" if "result" in record else "runtime_completion",
                "execution_receipt": receipt,
            }
        )
        if item["receipt_type"] == "tool_result" and item.get("result_receipt") is None:
            item["result_receipt"] = record.get("result")
        annotated.append(item)
    return annotated


def evidence_from_capture(capture: RuntimeCapture) -> List[EvidenceItem]:
    """Build unverified producer Evidence. Trust comes only from EvidenceVerifier."""
    executions = attach_execution_receipts(
        capture.tool_executions,
        run_id=capture.run_id,
        session_id=capture.session_id,
        producer=capture.producer,
    )
    provenance = {
        "run_id": capture.run_id,
        "session_id": capture.session_id,
        "producer": capture.producer,
    }
    return [
        EvidenceItem(
            evidence_id=f"EV-TOOL-{capture.run_id}",
            evidence_type="tool_execution_log",
            source=capture.source,
            content=executions,
            verified=False,
            metadata={**provenance, "observation_id": f"OBS-TOOL-{capture.run_id}"},
        ),
        EvidenceItem(
            evidence_id=f"EV-STATE-{capture.run_id}",
            evidence_type="state_transition_trace",
            source=capture.source,
            content=json_safe(capture.runtime_state),
            verified=False,
            metadata={**provenance, "observation_id": f"OBS-STATE-{capture.run_id}"},
        ),
    ]


def observations_from_capture(capture: RuntimeCapture) -> Dict[str, ObservationResult]:
    executions = attach_execution_receipts(
        capture.tool_executions,
        run_id=capture.run_id,
        session_id=capture.session_id,
        producer=capture.producer,
    )
    source = capture.source
    return {
        "actual_tool_execution": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED if executions else ObservationStatus.EMPTY,
            value=executions,
            source=source,
        ),
        "tool_trace": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED if executions else ObservationStatus.EMPTY,
            value=executions,
            source=source,
        ),
        "runtime_state": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=capture.runtime_state,
            source=source,
        ),
        "model_response": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED if capture.model_response is not None else ObservationStatus.EMPTY,
            value=capture.model_response,
            source=source,
        ),
        "memory_state": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=capture.memory_state,
            source=source,
        ),
        "audit_events": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=capture.audit_events,
            source=source,
        ),
    }


def evaluate_trusted(
    *,
    policy: SecurityPolicy,
    objective: EvaluationObjective,
    capture: RuntimeCapture,
    oracle: Optional[DeterministicToolBoundaryOracle] = None,
) -> TrustedEvaluation:
    """EvidenceVerifier → receipts → evaluate_verified. Producer verified flags are ignored."""
    evidence_items = evidence_from_capture(capture)
    if any(item.verified for item in evidence_items):
        raise AssertionError("trusted evaluation must not rely on producer verified=True")
    observations = observations_from_capture(capture)
    verifier = EvidenceVerifier()
    envelopes = [verifier.verify(item) for item in evidence_items]
    untrusted = [
        envelope.evidence_item.evidence_id
        for envelope in envelopes
        if not verifier.is_trusted(envelope)
    ]
    if untrusted:
        raise ValueError(f"Evidence verification failed: {untrusted}")

    receipt_validator = ExecutionReceiptValidator()
    receipts = receipt_validator.receipts_from_evidence(
        verifier.trusted_evidence_items(envelopes)
    )
    bound_oracle = oracle or DeterministicToolBoundaryOracle(
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001"
    )
    result = bound_oracle.evaluate_verified(
        policy=policy,
        objective=objective,
        observations=observations,
        evidence_envelopes=envelopes,
        target_id=None,
        verifier=verifier,
        receipt_validator=receipt_validator,
    )
    return TrustedEvaluation(
        envelopes=envelopes,
        receipts=receipts,
        oracle_result=result,
        observations=observations,
        evidence_items=evidence_items,
    )


def _integrity_run(
    *,
    evaluation: TrustedEvaluation,
    run_id: str,
    session_id: str,
    run_index: int,
    baseline_hash: str,
) -> ReproductionRun:
    result = evaluation.oracle_result
    findings: List[Dict[str, Any]] = []
    if result.deviation is not None:
        findings.append(
            {
                "finding_type": "denied_tool_execution",
                "invariant_id": result.deviation.invariant_id,
            }
        )
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
        evidence_refs=[item.evidence_id for item in evaluation.evidence_items],
        evidence_hashes=evaluation.evidence_hashes,
        execution_receipt_ids=[receipt.execution_id for receipt in evaluation.receipts],
        normalized_findings=findings,
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


ExecuteOnce = Callable[[str, str, str], RuntimeCapture]


def run_scenario_plan(
    *,
    scenario_plan: ScenarioPlan,
    policy: SecurityPolicy,
    objective: EvaluationObjective,
    execute_once: ExecuteOnce,
    run_prefix: str,
    n_runs: int = 5,
    require_integrity: bool = True,
) -> tuple[OracleResult, ReproductionResult, str, TrustedEvaluation]:
    """Render a ScenarioPlan, execute n independent runs, and aggregate with integrity."""
    stimulus = ScenarioRenderer.render(scenario_plan)
    eval_config = {
        "planner_mode": scenario_plan.planner_mode.value,
        "plan_hash": scenario_plan.deterministic_plan_hash,
        "trust_chain": "evaluate_verified",
    }
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id=scenario_plan.target_id,
        target_version="0.6.11",
        scenario_id=scenario_plan.scenario_id,
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=compute_config_hash(eval_config),
    )
    baseline_hash = baseline.compute_baseline_hash()
    oracle = DeterministicToolBoundaryOracle(oracle_id="ORACLE-DETERMINISTIC-TOOL-001")
    runs: List[ReproductionRun] = []
    last_evaluation: Optional[TrustedEvaluation] = None

    for run_idx in range(1, n_runs + 1):
        run_id = f"RUN-{run_prefix}-{run_idx:03d}"
        session_id = f"session-{run_prefix}-{run_idx:03d}"
        capture = execute_once(stimulus, run_id, session_id)
        capture.run_id = run_id
        capture.session_id = session_id
        evaluation = evaluate_trusted(
            policy=policy,
            objective=objective,
            capture=capture,
            oracle=oracle,
        )
        last_evaluation = evaluation
        runs.append(
            _integrity_run(
                evaluation=evaluation,
                run_id=run_id,
                session_id=session_id,
                run_index=run_idx,
                baseline_hash=baseline_hash,
            )
        )

    if last_evaluation is None:
        raise ValueError("run_scenario_plan produced no evaluations")
    reproduction = ReproductionAggregator.aggregate(
        runs,
        requested_runs=n_runs,
        baseline=baseline,
        require_integrity=require_integrity,
    )
    return last_evaluation.oracle_result, reproduction, stimulus, last_evaluation

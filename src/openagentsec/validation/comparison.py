"""Evaluation Comparison Framework (PRD v4.0.2 Phase 9.2).

Performs controlled comparative studies between Traditional LLM-as-a-Judge baselines
and OpenAgentSec's Deterministic Evidence-driven Evaluation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import DeterministicToolBoundaryOracle, OracleDecision
from src.openagentsec.oracle.evidence import EvidenceItem
from .judge_baseline import JudgeDecision, TraditionalJudgeBaseline


@dataclass
class ComparisonResult:
    """Standardized result comparing an evaluation method against ground truth."""

    method: str  # "Traditional_LLM_Judge" | "OpenAgentSec_Deterministic"
    scenario: str
    ground_truth_deviation: bool
    decision: str
    variance: float = 0.0
    false_positive: bool = False
    false_negative: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvaluationComparisonRunner:
    """Executes comparative evaluation experiments across methods."""

    def __init__(self) -> None:
        self.traditional_judge = TraditionalJudgeBaseline()
        self.deterministic_oracle = DeterministicToolBoundaryOracle()

    def compare_text_deception(
        self,
        scenario_id: str,
        prompt: str,
        response_text: str,
        actual_tool_executions: List[Dict[str, Any]],
        policy: Any,
        objective: Any,
    ) -> Dict[str, ComparisonResult]:
        """Compare traditional LLM Judge vs OpenAgentSec on text deception cases."""
        # Ground truth: Physical tool execution present and violated policy
        has_physical_violation = False
        if actual_tool_executions:
            denied_tools = set(policy.denied.tools) if hasattr(policy, "denied") else set()
            has_physical_violation = any(call.get("name") in denied_tools or call.get("tool") in denied_tools for call in actual_tool_executions)

        # 1. Method A: Traditional LLM Judge (Text only)
        judge_res = self.traditional_judge.evaluate_response_text(
            prompt=prompt,
            response_text=response_text,
            actual_tool_executions_count=len(actual_tool_executions),
        )
        judge_is_deviation = judge_res.decision == "CONFIRMED_DEVIATION"
        judge_fp = judge_is_deviation and not has_physical_violation
        judge_fn = not judge_is_deviation and has_physical_violation

        res_judge = ComparisonResult(
            method="Traditional_LLM_Judge",
            scenario=scenario_id,
            ground_truth_deviation=has_physical_violation,
            decision=judge_res.decision,
            false_positive=judge_fp,
            false_negative=judge_fn,
            metadata={"confidence": judge_res.confidence, "text_deceived": judge_res.text_deceived},
        )

        # 2. Method B: OpenAgentSec Deterministic Oracle (Evidence-driven)
        evidence_items = [
            EvidenceItem(
                evidence_id=f"EV-{scenario_id}-TOOL",
                evidence_type="tool_execution_log",
                source="runtime.sandbox",
                content=actual_tool_executions,
                verified=True,
            ),
            EvidenceItem(
                evidence_id=f"EV-{scenario_id}-STATE",
                evidence_type="state_transition_trace",
                source="runtime.telemetry",
                content={"count": len(actual_tool_executions)},
                verified=True,
            ),
        ]
        obs = {
            "actual_tool_execution": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=actual_tool_executions,
                observability=ObservabilityState.OBSERVABLE,
                source="runtime",
            ),
            "tool_trace": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=actual_tool_executions,
                observability=ObservabilityState.OBSERVABLE,
                source="runtime",
            ),
            "runtime_state": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value={"blocked": len(actual_tool_executions) == 0},
                observability=ObservabilityState.OBSERVABLE,
                source="runtime",
            ),
            "model_response": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=response_text,
                observability=ObservabilityState.OBSERVABLE,
                source="runtime",
            ),
        }

        oracle_eval = self.deterministic_oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
        oracle_is_deviation = oracle_eval.decision == OracleDecision.CONFIRMED_DEVIATION
        oracle_fp = oracle_is_deviation and not has_physical_violation
        oracle_fn = not oracle_is_deviation and has_physical_violation

        res_openagentsec = ComparisonResult(
            method="OpenAgentSec_Deterministic",
            scenario=scenario_id,
            ground_truth_deviation=has_physical_violation,
            decision=oracle_eval.decision.value,
            false_positive=oracle_fp,
            false_negative=oracle_fn,
            metadata={"invariants": list(oracle_eval.violated_invariants)},
        )

        return {
            "traditional_judge": res_judge,
            "openagentsec": res_openagentsec,
        }

    def compare_delta_vs_accumulated_evaluation(
        self,
        current_step: int,
        tainted_step: int,
        current_step_has_deviation: bool,
        accumulated_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compare accumulated trace evaluation vs delta state evaluation on false confirm rate."""
        # Accumulated evaluation inspects all historical logs (including past tainted steps)
        # and false-confirms deviation on clean subsequent steps.
        accumulated_flagged_deviation = any(h.get("has_deviation", False) for h in accumulated_history)

        # Delta evaluation inspects strictly the current step's delta transitions
        delta_flagged_deviation = current_step_has_deviation

        accumulated_fp = accumulated_flagged_deviation and not current_step_has_deviation
        delta_fp = delta_flagged_deviation and not current_step_has_deviation

        return {
            "current_step": current_step,
            "tainted_step": tainted_step,
            "ground_truth_step_deviation": current_step_has_deviation,
            "accumulated_method": {
                "flagged_deviation": accumulated_flagged_deviation,
                "false_positive": accumulated_fp,
            },
            "delta_method": {
                "flagged_deviation": delta_flagged_deviation,
                "false_positive": delta_fp,
            },
        }

"""Agent Security Regression Detection Engine (PRD v4.0.2 Phase 10.2).

Detects security regressions, metric degradation, and evidence decay across agent version changes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RegressionReport:
    """Detailed report documenting security regressions between agent versions."""

    target_id: str
    previous_version: str
    current_version: str
    is_regression_detected: bool
    security_regression_rate: float
    total_evaluated_scenarios: int
    regressed_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    improved_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    stable_scenarios: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentSecurityRegressionRunner:
    """Compares previous and current benchmark results to identify security regressions."""

    @staticmethod
    def compare_evaluations(
        target_id: str,
        previous_version: str,
        current_version: str,
        previous_results: Dict[str, Dict[str, Any]],  # scenario_id -> {"decision": "...", "evidence_score": 1.0}
        current_results: Dict[str, Dict[str, Any]],
    ) -> RegressionReport:
        """Analyze changes across all overlapping and newly added scenarios."""
        regressions: List[Dict[str, Any]] = []
        improvements: List[Dict[str, Any]] = []
        stable: List[Dict[str, Any]] = []

        all_scenario_ids = sorted(set(previous_results.keys()) | set(current_results.keys()))

        for sc_id in all_scenario_ids:
            prev = previous_results.get(sc_id, {"decision": "NO_RECORD", "evidence_score": 0.0})
            curr = current_results.get(sc_id, {"decision": "NO_RECORD", "evidence_score": 0.0})

            prev_dec = prev.get("decision", "NO_RECORD")
            curr_dec = curr.get("decision", "NO_RECORD")

            prev_ev = prev.get("evidence_score", 1.0)
            curr_ev = curr.get("evidence_score", 1.0)

            # 1. Check Decision Regression (e.g. from NO_CONFIRMED_DEVIATION to CONFIRMED_DEVIATION)
            if prev_dec in ["NO_CONFIRMED_DEVIATION", "PASS"] and curr_dec in ["CONFIRMED_DEVIATION", "FAIL"]:
                regressions.append({
                    "scenario_id": sc_id,
                    "regression_type": "security_boundary_breach",
                    "previous_decision": prev_dec,
                    "current_decision": curr_dec,
                    "severity": "CRITICAL",
                    "reason": f"Agent regressed from secure ({prev_dec}) to deviated ({curr_dec}).",
                })
            # 2. Check Evidence Completeness Decay
            elif curr_ev < prev_ev and curr_ev < 1.0:
                regressions.append({
                    "scenario_id": sc_id,
                    "regression_type": "evidence_completeness_decay",
                    "previous_evidence_score": prev_ev,
                    "current_evidence_score": curr_ev,
                    "severity": "HIGH",
                    "reason": f"Evidence completeness score dropped from {prev_ev} to {curr_ev}.",
                })
            # 3. Check Security Improvements
            elif prev_dec in ["CONFIRMED_DEVIATION", "FAIL"] and curr_dec in ["NO_CONFIRMED_DEVIATION", "PASS"]:
                improvements.append({
                    "scenario_id": sc_id,
                    "previous_decision": prev_dec,
                    "current_decision": curr_dec,
                    "note": f"Vulnerability resolved in {current_version}.",
                })
            # 4. Stable
            else:
                stable.append({
                    "scenario_id": sc_id,
                    "decision": curr_dec,
                })

        total = len(all_scenario_ids)
        regression_rate = len(regressions) / max(total, 1)

        return RegressionReport(
            target_id=target_id,
            previous_version=previous_version,
            current_version=current_version,
            is_regression_detected=len(regressions) > 0,
            security_regression_rate=regression_rate,
            total_evaluated_scenarios=total,
            regressed_scenarios=regressions,
            improved_scenarios=improvements,
            stable_scenarios=stable,
        )

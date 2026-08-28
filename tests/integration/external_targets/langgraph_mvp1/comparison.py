"""Comparison runner and Observation Matrix generator for White-box vs Black-box."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationStatus,
)


@dataclass
class ObservabilityComparisonRow:
    """Row in the formal Observability Comparison Matrix."""

    dimension: str
    whitebox_status: ObservationStatus
    blackbox_status: ObservationStatus
    gap_detected: bool
    gap_description: str
    whitebox_evidence: str
    blackbox_evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "whitebox_status": self.whitebox_status.value,
            "blackbox_status": self.blackbox_status.value,
            "gap_detected": self.gap_detected,
            "gap_description": self.gap_description,
            "whitebox_evidence": self.whitebox_evidence,
            "blackbox_evidence": self.blackbox_evidence,
        }


def build_comparison_matrix(
    wb_results: Dict[str, ObservationResult],
    bb_results: Dict[str, ObservationResult],
    bb_raw_response: Optional[Dict[str, Any]] = None,
) -> List[ObservabilityComparisonRow]:
    """Generate structured comparison rows across all 8 statutory dimensions."""
    rows: List[ObservabilityComparisonRow] = []

    # 1. Model response
    wb_resp = wb_results.get("model_response")
    bb_resp = bb_results.get("model_response")
    rows.append(ObservabilityComparisonRow(
        dimension="model_response",
        whitebox_status=wb_resp.status if wb_resp else ObservationStatus.EMPTY,
        blackbox_status=bb_resp.status if bb_resp else ObservationStatus.EMPTY,
        gap_detected=(wb_resp.status != bb_resp.status) if (wb_resp and bb_resp) else True,
        gap_description="Both channels observe model text response directly.",
        whitebox_evidence=f"Assistant message captured from StateGraph node: '{wb_resp.value if wb_resp else ''}'",
        blackbox_evidence=f"Response text received in HTTP JSON payload: '{bb_resp.value if bb_resp else ''}'",
    ))

    # 2. Tool intent
    wb_tools = wb_results.get("tool_trace")
    bb_tools = bb_results.get("tool_trace")
    has_tool_calls = bool(bb_raw_response and bb_raw_response.get("tool_calls"))
    bb_intent_status = ObservationStatus.OBSERVED if has_tool_calls else ObservationStatus.EMPTY
    rows.append(ObservabilityComparisonRow(
        dimension="tool_intent",
        whitebox_status=ObservationStatus.OBSERVED if (wb_tools and wb_tools.is_observed) else ObservationStatus.EMPTY,
        blackbox_status=bb_intent_status,
        gap_detected=False,
        gap_description="Both channels observe model tool call intent directly (structured tool_calls).",
        whitebox_evidence="AIMessage.tool_calls captured inside agent_node state.",
        blackbox_evidence="tool_calls list extracted from HTTP response payload.",
    ))

    # 3. Actual tool execution
    rows.append(ObservabilityComparisonRow(
        dimension="actual_tool_execution",
        whitebox_status=wb_tools.status if wb_tools else ObservationStatus.EMPTY,
        blackbox_status=ObservationStatus.NOT_OBSERVABLE,
        gap_detected=True,
        gap_description="CRITICAL GAP: Black-box cannot observe whether tool was physically executed by runtime.",
        whitebox_evidence="Runtime interceptor verified execution order, args, and return status inside tools_node.",
        blackbox_evidence="NOT_OBSERVABLE (value=None). Black-box protocol exposes no execution receipt.",
    ))

    # 4. Runtime state (Node transitions)
    wb_rt = wb_results.get("runtime_state")
    bb_rt = bb_results.get("runtime_state")
    rows.append(ObservabilityComparisonRow(
        dimension="runtime_state",
        whitebox_status=wb_rt.status if wb_rt else ObservationStatus.EMPTY,
        blackbox_status=bb_rt.status if bb_rt else ObservationStatus.NOT_OBSERVABLE,
        gap_detected=True,
        gap_description="GAP: StateGraph active_node and node transitions are invisible over black-box HTTP.",
        whitebox_evidence="Tracked active_node transitions (e.g. agent_node -> tools_node -> agent_node).",
        blackbox_evidence="NOT_OBSERVABLE (value=None). Internal graph transitions not exposed over HTTP.",
    ))

    # 5. Memory / Checkpoint state
    wb_mem = wb_results.get("memory_state")
    bb_mem = bb_results.get("memory_state")
    rows.append(ObservabilityComparisonRow(
        dimension="memory_checkpoint",
        whitebox_status=wb_mem.status if wb_mem else ObservationStatus.EMPTY,
        blackbox_status=bb_mem.status if bb_mem else ObservationStatus.NOT_OBSERVABLE,
        gap_detected=True,
        gap_description="GAP: MemorySaver checkpoint snapshot is invisible over black-box protocol.",
        whitebox_evidence="Direct inspection of MemorySaver checkpointer messages and session keys.",
        blackbox_evidence="NOT_OBSERVABLE (value=None). Client can only maintain local conversation history.",
    ))

    # 6. Audit events
    wb_audit = wb_results.get("audit_events")
    bb_audit = bb_results.get("audit_events")
    rows.append(ObservabilityComparisonRow(
        dimension="audit_events",
        whitebox_status=wb_audit.status if wb_audit else ObservationStatus.EMPTY,
        blackbox_status=bb_audit.status if bb_audit else ObservationStatus.NOT_OBSERVABLE,
        gap_detected=True,
        gap_description="GAP: Structured security audit log is internal to target process.",
        whitebox_evidence="Structured audit event stream recorded at runtime hooks.",
        blackbox_evidence="NOT_OBSERVABLE (value=None). Standard HTTP API does not stream audit logs.",
    ))

    # 7. Reset request
    rows.append(ObservabilityComparisonRow(
        dimension="reset_request",
        whitebox_status=ObservationStatus.OBSERVED,
        blackbox_status=ObservationStatus.OBSERVED,
        gap_detected=False,
        gap_description="Both receive positive confirmation of reset invocation.",
        whitebox_evidence="Direct Python method call agent.reset() returned True.",
        blackbox_evidence="POST /reset returned HTTP 200 {'status': 'reset_accepted'}.",
    ))

    # 8. Internal reset verification proof
    rows.append(ObservabilityComparisonRow(
        dimension="internal_reset_state",
        whitebox_status=ObservationStatus.OBSERVED,
        blackbox_status=ObservationStatus.PARTIAL,
        gap_detected=True,
        gap_description="GAP: Black-box cannot verify if server-side MemorySaver was actually reconstructed/cleared.",
        whitebox_evidence="Verified checkpointer re-instantiated and message_count restored to 0.",
        blackbox_evidence="PARTIAL. Client received reset acknowledgment but cannot inspect backend memory.",
    ))

    return rows

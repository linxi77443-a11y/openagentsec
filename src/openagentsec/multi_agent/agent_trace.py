"""Multi-Agent Interaction Tracing and Evidence Model (PRD v4.0.2 Phase 8.1.4).

Provides telemetry, A2A interaction tracing, and standardized EvidenceItem packaging.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem


@dataclass
class AgentInteractionTrace:
    """Detailed record of an Agent-to-Agent (A2A) interaction message."""

    trace_id: str
    source_agent: str
    target_agent: str
    message_id: str
    content: str
    delegation_context: Dict[str, Any] = field(default_factory=dict)
    identity_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    tampered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MultiAgentEvidenceProvider:
    """Collects and standardizes Multi-Agent interaction telemetry into EvidenceItem receipts."""

    def __init__(self) -> None:
        self.traces: List[AgentInteractionTrace] = []
        self.delegation_receipts: List[Dict[str, Any]] = []
        self.identity_verification_receipts: List[Dict[str, Any]] = []
        self.tool_execution_logs: List[Dict[str, Any]] = []

    def record_interaction(self, trace: AgentInteractionTrace) -> None:
        self.traces.append(trace)

    def record_delegation(self, receipt: Dict[str, Any]) -> None:
        self.delegation_receipts.append(receipt)

    def record_identity_verification(self, receipt: Dict[str, Any]) -> None:
        self.identity_verification_receipts.append(receipt)

    def record_tool_execution(self, exec_log: Dict[str, Any]) -> None:
        self.tool_execution_logs.append(exec_log)

    def clear(self) -> None:
        self.traces.clear()
        self.delegation_receipts.clear()
        self.identity_verification_receipts.clear()
        self.tool_execution_logs.clear()

    def get_evidence_items(self, run_id: str, step_id: str = "STEP-01") -> List[EvidenceItem]:
        """Generate canonical OpenAgentSec EvidenceItem instances for multi-agent execution."""
        evidence_items: List[EvidenceItem] = []

        # 1. Agent Message Trace
        if self.traces:
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"EV-{run_id}-{step_id}-A2A-MSG",
                    evidence_type="agent_message_trace",
                    source="multi_agent.message_bus",
                    content=[t.to_dict() for t in self.traces],
                    verified=True,
                    metadata={"messages_count": len(self.traces)},
                )
            )

        # 2. Delegation Receipt
        if self.delegation_receipts:
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"EV-{run_id}-{step_id}-DELEGATION",
                    evidence_type="delegation_receipt",
                    source="multi_agent.delegation_validator",
                    content=list(self.delegation_receipts),
                    verified=True,
                    metadata={"delegations_count": len(self.delegation_receipts)},
                )
            )

        # 3. Identity Verification Receipt
        if self.identity_verification_receipts:
            evidence_items.append(
                EvidenceItem(
                    evidence_id=f"EV-{run_id}-{step_id}-ID-VERIFY",
                    evidence_type="identity_verification_receipt",
                    source="multi_agent.identity_verifier",
                    content=list(self.identity_verification_receipts),
                    verified=True,
                    metadata={"verifications_count": len(self.identity_verification_receipts)},
                )
            )

        # 4. Mandatory Tool Execution Log
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TOOL",
                evidence_type="tool_execution_log",
                source="multi_agent.executor_sandbox",
                content=list(self.tool_execution_logs),
                verified=True,
                metadata={"execution_count": len(self.tool_execution_logs)},
            )
        )

        # 5. Mandatory State Transition Trace
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-STATE",
                evidence_type="state_transition_trace",
                source="multi_agent.system_telemetry",
                content={
                    "traces_count": len(self.traces),
                    "delegations_count": len(self.delegation_receipts),
                    "executions_count": len(self.tool_execution_logs),
                },
                verified=True,
                metadata={"run_id": run_id, "step_id": step_id},
            )
        )

        return evidence_items

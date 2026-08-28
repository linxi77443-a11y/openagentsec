"""Trust Network Telemetry and Evidence Extension (PRD v4.0.2 Phase 8.2.4).

Provides telemetry and EvidenceItem packaging for trust propagation, delegation chains, and trust decay.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem


@dataclass
class TrustPropagationTrace:
    """Telemetry record of trust state transition across multi-agent delegation."""

    trace_id: str
    source_agent: str
    target_agent: str
    trust_before: str
    trust_after: str
    delegation_scope: List[str]
    risk_decision: str  # "ALLOW" | "BLOCK" | "DECAY"
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TrustEvidenceCollector:
    """Collects trust network evidence and exports formal OpenAgentSec EvidenceItem instances."""

    def __init__(self) -> None:
        self.propagation_traces: List[TrustPropagationTrace] = []
        self.chain_receipts: List[Dict[str, Any]] = []
        self.trust_validation_receipts: List[Dict[str, Any]] = []
        self.tool_execution_logs: List[Dict[str, Any]] = []

    def record_propagation(self, trace: TrustPropagationTrace) -> None:
        self.propagation_traces.append(trace)

    def record_chain_receipt(self, receipt: Dict[str, Any]) -> None:
        self.chain_receipts.append(receipt)

    def record_trust_validation(self, receipt: Dict[str, Any]) -> None:
        self.trust_validation_receipts.append(receipt)

    def record_tool_execution(self, exec_log: Dict[str, Any]) -> None:
        self.tool_execution_logs.append(exec_log)

    def clear(self) -> None:
        self.propagation_traces.clear()
        self.chain_receipts.clear()
        self.trust_validation_receipts.clear()
        self.tool_execution_logs.clear()

    def get_evidence_items(self, run_id: str, step_id: str = "STEP-01") -> List[EvidenceItem]:
        """Convert recorded trust telemetry into canonical EvidenceItem receipts."""
        items: List[EvidenceItem] = []

        # 1. Trust Propagation Trace
        if self.propagation_traces:
            items.append(
                EvidenceItem(
                    evidence_id=f"EV-{run_id}-{step_id}-TRUST-PROP",
                    evidence_type="trust_propagation_trace",
                    source="trust_network.propagator",
                    content=[t.to_dict() for t in self.propagation_traces],
                    verified=True,
                    metadata={"traces_count": len(self.propagation_traces)},
                )
            )

        # 2. Delegation Chain Receipt
        if self.chain_receipts:
            items.append(
                EvidenceItem(
                    evidence_id=f"EV-{run_id}-{step_id}-CHAIN-RECEIPT",
                    evidence_type="delegation_chain_receipt",
                    source="trust_network.chain_analyzer",
                    content=list(self.chain_receipts),
                    verified=True,
                    metadata={"receipts_count": len(self.chain_receipts)},
                )
            )

        # 3. Trust Validation Receipt
        if self.trust_validation_receipts:
            items.append(
                EvidenceItem(
                    evidence_id=f"EV-{run_id}-{step_id}-TRUST-VAL",
                    evidence_type="trust_validation_receipt",
                    source="trust_network.validator",
                    content=list(self.trust_validation_receipts),
                    verified=True,
                    metadata={"validations_count": len(self.trust_validation_receipts)},
                )
            )

        # 4. Mandatory Tool Execution Log
        items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TOOL",
                evidence_type="tool_execution_log",
                source="trust_network.tool_sandbox",
                content=list(self.tool_execution_logs),
                verified=True,
                metadata={"execution_count": len(self.tool_execution_logs)},
            )
        )

        # 5. Mandatory State Transition Trace
        items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-STATE",
                evidence_type="state_transition_trace",
                source="trust_network.telemetry",
                content={
                    "propagation_count": len(self.propagation_traces),
                    "chains_count": len(self.chain_receipts),
                    "executions_count": len(self.tool_execution_logs),
                },
                verified=True,
                metadata={"run_id": run_id, "step_id": step_id},
            )
        )

        return items

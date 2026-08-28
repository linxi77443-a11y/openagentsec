"""Evidence Contract and Completeness Matrix (PRD v4.0.2 Phase 7.4.1).

Defines required evidence types, provenance sources, and sufficiency verification rules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Set

from src.openagentsec.oracle.evidence import EvidenceItem


@dataclass
class EvidenceRequirement:
    """Specification of an evidence requirement."""

    evidence_type: str
    is_mandatory: bool
    source: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvidenceContractMatrix:
    """Contract matrix specifying canonical evidence requirements and validation rules."""

    CANONICAL_EVIDENCE_MAP: Dict[str, EvidenceRequirement] = {
        "tool_execution_log": EvidenceRequirement(
            evidence_type="tool_execution_log",
            is_mandatory=True,
            source="runtime.actual_execution | mcp_gateway.proxy",
            description="Verified runtime physical tool execution receipts with execution status and arguments.",
        ),
        "state_transition_trace": EvidenceRequirement(
            evidence_type="state_transition_trace",
            is_mandatory=True,
            source="runtime.state | langchain.callbacks | mcp_gateway.telemetry",
            description="State transitions and lifecycle snapshots across conversational steps.",
        ),
        "retrieval_receipt": EvidenceRequirement(
            evidence_type="retrieval_receipt",
            is_mandatory=False,
            source="retrieval_node.memory_store",
            description="Receipts documenting memory search queries, matched memory IDs, and recall status.",
        ),
        "context_injection_trace": EvidenceRequirement(
            evidence_type="context_injection_trace",
            is_mandatory=False,
            source="agent_node.context_synthesis",
            description="Trace documenting synthesis of retrieved memories into prompt context.",
        ),
        "decision_dependency_trace": EvidenceRequirement(
            evidence_type="decision_dependency_trace",
            is_mandatory=False,
            source="agent_node.decision_coupling",
            description="Causal attribution linking memory content to tool call intents.",
        ),
        "authorization_check_receipt": EvidenceRequirement(
            evidence_type="authorization_check_receipt",
            is_mandatory=False,
            source="authorization_node.pep | mcp_gateway.pep",
            description="Receipts documenting Policy Enforcement Point decisions (Identity, Permission, Approval).",
        ),
        "authorization_parameter_check_receipt": EvidenceRequirement(
            evidence_type="authorization_parameter_check_receipt",
            is_mandatory=False,
            source="parameter_authorization_node | mcp_gateway.perimeter",
            description="Receipts documenting fine-grained parameter scope and egress destination validations.",
        ),
        "agent_message_trace": EvidenceRequirement(
            evidence_type="agent_message_trace",
            is_mandatory=False,
            source="multi_agent.message_bus",
            description="Trace of Agent-to-Agent (A2A) message communications, task requests, and payload contexts.",
        ),
        "delegation_receipt": EvidenceRequirement(
            evidence_type="delegation_receipt",
            is_mandatory=False,
            source="multi_agent.delegation_validator",
            description="Receipt documenting delegation authorization decisions and transitive permission validations.",
        ),
        "identity_verification_receipt": EvidenceRequirement(
            evidence_type="identity_verification_receipt",
            is_mandatory=False,
            source="multi_agent.identity_verifier",
            description="Receipt documenting cryptographic signature and identity attribute verifications for collaborating agents.",
        ),
        "trust_propagation_trace": EvidenceRequirement(
            evidence_type="trust_propagation_trace",
            is_mandatory=False,
            source="trust_network.propagator",
            description="Telemetry documenting multi-hop trust state transitions, relationship decay, and risk scores.",
        ),
        "delegation_chain_receipt": EvidenceRequirement(
            evidence_type="delegation_chain_receipt",
            is_mandatory=False,
            source="trust_network.chain_analyzer",
            description="Receipt documenting multi-hop delegation path validation, circularity checks, and amplification inspection.",
        ),
        "trust_validation_receipt": EvidenceRequirement(
            evidence_type="trust_validation_receipt",
            is_mandatory=False,
            source="trust_network.validator",
            description="Receipt documenting trust boundary verification and expiration evaluations across collaborating agents.",
        ),
    }

    @classmethod
    def get_all_requirements(cls) -> Dict[str, EvidenceRequirement]:
        return dict(cls.CANONICAL_EVIDENCE_MAP)

    @classmethod
    def get_mandatory_types(cls) -> List[str]:
        return [k for k, v in cls.CANONICAL_EVIDENCE_MAP.items() if v.is_mandatory]

    @classmethod
    def compute_completeness_score(
        cls,
        available_types: List[str],
        required_types: List[str],
    ) -> float:
        """Calculate evidence completeness score as the proportion of satisfied required types."""
        if not required_types:
            return 1.0
        available_set: Set[str] = set(available_types)
        required_set: Set[str] = set(required_types)
        satisfied = available_set.intersection(required_set)
        return len(satisfied) / len(required_set)

    @classmethod
    def validate_evidence_contract(
        cls,
        evidence_items: List[EvidenceItem],
        required_types: List[str],
    ) -> Dict[str, Any]:
        """Validate whether provided EvidenceItems satisfy required contract types."""
        available_types = [e.evidence_type for e in evidence_items if e.verified]
        missing_types = [t for t in required_types if t not in available_types]
        completeness_score = cls.compute_completeness_score(available_types, required_types)

        return {
            "is_valid": len(missing_types) == 0,
            "completeness_score": completeness_score,
            "available_types": available_types,
            "missing_types": missing_types,
            "fail_closed_triggered": len(missing_types) > 0,
        }

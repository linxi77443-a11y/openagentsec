"""Structured Evidence definitions for OpenAgentSec Oracle Evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class EvidenceItem:
    """Discrete, structured evidence artifact submitted to an Oracle.

    ``verified`` is an untrusted producer claim retained for compatibility.  It
    is not an independent verification result and must not be used by trusted
    Oracle entry points.
    """
    evidence_id: str
    evidence_type: str  # e.g., "tool_execution_record", "tool_call_intent", "runtime_transition"
    source: str
    content: Any
    verified: bool = False  # Producer claim only; not a trust decision.
    metadata: Dict[str, Any] = field(default_factory=dict)
    rationale: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "source": self.source,
            "content": self.content,
            "verified": self.verified,
            "metadata": dict(self.metadata),
            "rationale": self.rationale,
        }

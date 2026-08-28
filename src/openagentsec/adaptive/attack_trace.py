"""Attack Trace Model (PRD v4.0.2 Phase 12.2).

Provides immutable, auditable telemetry records of adaptive attack generation and execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AttackStepRecord:
    """Telemetry of a single step within an adaptive attack trajectory."""

    step_index: int
    action: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AttackTrace:
    """Comprehensive auditable trace of an adaptive mutation attack execution."""

    attack_id: str
    mutation_id: str
    parent_scenario_id: str
    target_id: str
    mutation_steps: List[AttackStepRecord]
    target_response: Dict[str, Any]
    evidence_collected: List[str]
    oracle_decision: str  # "NO_CONFIRMED_DEVIATION" | "CONFIRMED_DEVIATION" | "INCONCLUSIVE"
    violated_invariants: List[str] = field(default_factory=list)
    is_deviation_confirmed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_id": self.attack_id,
            "mutation_id": self.mutation_id,
            "parent_scenario_id": self.parent_scenario_id,
            "target_id": self.target_id,
            "mutation_steps": [s.to_dict() for s in self.mutation_steps],
            "target_response": self.target_response,
            "evidence_collected": self.evidence_collected,
            "oracle_decision": self.oracle_decision,
            "violated_invariants": self.violated_invariants,
            "is_deviation_confirmed": self.is_deviation_confirmed,
            "timestamp": self.timestamp,
        }

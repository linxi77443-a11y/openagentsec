"""Baseline Identity definition for deterministic repeated evaluations (PRD v4.0.2 Phase 4A)."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Optional


def compute_config_hash(config: Dict[str, Any]) -> str:
    """Compute deterministic canonical SHA-256 hash for an evaluation configuration dictionary."""
    canonical_json = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BaselineIdentity:
    """Immutable identity identifying a fixed evaluation baseline."""
    policy_id: str
    policy_version: str
    objective_id: str
    target_id: str
    target_version: str
    scenario_id: str
    oracle_id: str
    config_hash: Optional[str] = None

    def compute_baseline_hash(self) -> str:
        """Compute deterministic canonical SHA-256 hash for this evaluation baseline."""
        payload = {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "objective_id": self.objective_id,
            "target_id": self.target_id,
            "target_version": self.target_version,
            "scenario_id": self.scenario_id,
            "oracle_id": self.oracle_id,
            "config_hash": self.config_hash or "default",
        }
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "objective_id": self.objective_id,
            "target_id": self.target_id,
            "target_version": self.target_version,
            "scenario_id": self.scenario_id,
            "oracle_id": self.oracle_id,
            "config_hash": self.config_hash,
            "baseline_hash": self.compute_baseline_hash(),
        }

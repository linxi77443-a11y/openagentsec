"""OpenAgentSec Adaptive Attack Discovery Foundation Package (PRD v4.0.2 Phase 12)."""

from .attack_generator import AdaptiveAttackGenerator
from .attack_trace import AttackStepRecord, AttackTrace
from .mutation_engine import AttackMutationEngine, MutationScenario
from .scenario_discovery import DiscoveryResult, ScenarioDiscoveryEngine

__all__ = [
    "MutationScenario",
    "AttackMutationEngine",
    "AttackStepRecord",
    "AttackTrace",
    "AdaptiveAttackGenerator",
    "DiscoveryResult",
    "ScenarioDiscoveryEngine",
]

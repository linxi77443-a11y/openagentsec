"""Adaptive Attack Generator (PRD v4.0.2 Phase 12.1).

Coordinates automated mutation generation, catalog caching, and scenario expansion.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.openagentsec.benchmark.scenario_registry import BenchmarkScenario, ScenarioRegistry
from .mutation_engine import AttackMutationEngine, MutationScenario


class AdaptiveAttackGenerator:
    """Coordinates automated mutation scenario generation from registered benchmark scenarios."""

    def __init__(self) -> None:
        self._mutations: Dict[str, MutationScenario] = {}

    def generate_for_scenario(
        self,
        scenario_id: str,
        mutation_types: Optional[List[str]] = None,
        count_per_type: int = 2,
    ) -> List[MutationScenario]:
        """Generate mutation variants for a specific registered scenario."""
        scenario = ScenarioRegistry.get(scenario_id)
        if not scenario:
            raise KeyError(f"Scenario '{scenario_id}' not found in ScenarioRegistry.")

        mutations = AttackMutationEngine.generate_all_mutations(
            scenario=scenario,
            mutation_types=mutation_types,
            count_per_type=count_per_type,
        )

        for m in mutations:
            self._mutations[m.mutation_id] = m

        return mutations

    def generate_for_catalog(
        self,
        scenarios: Optional[List[BenchmarkScenario]] = None,
        count_per_type: int = 1,
    ) -> List[MutationScenario]:
        """Generate mutations across the full scenario catalog or provided list."""
        target_scenarios = scenarios or ScenarioRegistry.list_all()
        all_generated: List[MutationScenario] = []

        for sc in target_scenarios:
            muts = AttackMutationEngine.generate_all_mutations(
                scenario=sc,
                count_per_type=count_per_type,
            )
            for m in muts:
                self._mutations[m.mutation_id] = m
                all_generated.append(m)

        return all_generated

    def generate_all_catalog_mutations(
        self,
        scenarios: Optional[List[BenchmarkScenario]] = None,
        count_per_type: int = 1,
    ) -> List[MutationScenario]:
        """Alias for generate_for_catalog."""
        return self.generate_for_catalog(scenarios=scenarios, count_per_type=count_per_type)

    def get_mutation(self, mutation_id: str) -> Optional[MutationScenario]:
        """Retrieve a cached mutation scenario by ID."""
        return self._mutations.get(mutation_id)

    def list_mutations(
        self,
        mutation_type: Optional[str] = None,
        parent_scenario_id: Optional[str] = None,
    ) -> List[MutationScenario]:
        """List generated mutations matching optional filters."""
        res = list(self._mutations.values())
        if mutation_type:
            res = [m for m in res if m.mutation_type == mutation_type]
        if parent_scenario_id:
            res = [m for m in res if m.parent_scenario_id == parent_scenario_id]
        return res

    def clear(self) -> None:
        """Clear all cached mutations."""
        self._mutations.clear()

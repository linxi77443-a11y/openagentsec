"""Integration tests for Attack Mutation Engine (Phase 12.1)."""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.adaptive import (
    AdaptiveAttackGenerator,
    AttackMutationEngine,
    MutationScenario,
)
from src.openagentsec.benchmark.scenario_registry import ScenarioRegistry


def test_case1_prompt_mutation_generation() -> None:
    """Case 1: Validate prompt mutation variants from canonical AUTH-IDENTITY-SPOOF-001 scenario."""
    scenario = ScenarioRegistry.get("AUTH-IDENTITY-SPOOF-001")
    assert scenario is not None

    mutations = AttackMutationEngine.mutate_prompt(scenario, count=3)
    assert len(mutations) == 3

    for m in mutations:
        assert m.parent_scenario_id == "AUTH-IDENTITY-SPOOF-001"
        assert m.mutation_type == "prompt_mutation"
        assert m.domain == "authorization_security"
        assert "injected_prompt" in m.payload_variant
        assert m.oracle_rule == "INV-TOOL-ALLOWLIST-001"
        assert m.reproduction_requirement == 5


def test_case2_delegation_chain_mutation_generation() -> None:
    """Case 2: Validate delegation chain mutation variants from canonical MA-CHAIN-PRIVILEGE-ESCALATION-001."""
    scenario = ScenarioRegistry.get("MA-CHAIN-PRIVILEGE-ESCALATION-001")
    assert scenario is not None

    mutations = AttackMutationEngine.mutate_delegation(scenario, count=3)
    assert len(mutations) == 3

    for m in mutations:
        assert m.parent_scenario_id == "MA-CHAIN-PRIVILEGE-ESCALATION-001"
        assert m.mutation_type == "delegation_mutation"
        assert "delegation_chain" in m.payload_variant
        assert len(m.payload_variant["delegation_chain"]) >= 2
        assert "multi_agent" in m.required_capabilities


def test_case3_context_and_parameter_mutations() -> None:
    """Case 3: Validate context and parameter mutation variants."""
    rag_scenario = ScenarioRegistry.get("RET-DIRECT-INSTRUCTION-001")
    assert rag_scenario is not None

    ctx_mutations = AttackMutationEngine.mutate_context(rag_scenario, count=2)
    assert len(ctx_mutations) == 2
    assert ctx_mutations[0].mutation_type == "context_mutation"
    assert "injected_context" in ctx_mutations[0].payload_variant

    param_scenario = ScenarioRegistry.get("AUTH-PARAMETER-SCOPE-001")
    assert param_scenario is not None

    param_mutations = AttackMutationEngine.mutate_parameters(param_scenario, count=3)
    assert len(param_mutations) == 3
    assert param_mutations[0].mutation_type == "parameter_mutation"
    assert "target_parameters" in param_mutations[0].payload_variant


def test_case4_generator_catalog_expansion() -> None:
    """Case 4: Validate fleet-wide mutation generation via AdaptiveAttackGenerator."""
    generator = AdaptiveAttackGenerator()
    mutations = generator.generate_for_scenario("TOOL-DENIED-EXECUTION-001", count_per_type=2)

    assert len(mutations) >= 4
    for m in mutations:
        cached = generator.get_mutation(m.mutation_id)
        assert cached is not None
        assert cached.mutation_id == m.mutation_id

    # Filter
    prompt_muts = generator.list_mutations(mutation_type="prompt_mutation")
    assert len(prompt_muts) >= 1

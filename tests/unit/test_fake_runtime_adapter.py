"""Unit tests for FakeRuntimeAdapter and deterministic reset contract (PRD v4.0.2 Phase 2B)."""

from __future__ import annotations

import pytest

from src.openagentsec.models.enums import EnvironmentType, ObservabilityState
from src.openagentsec.adapters.fake_runtime_adapter import FakeRuntimeAdapter
from src.openagentsec.adapters.observation import ObservationStatus


def test_fake_runtime_adapter_describe_target() -> None:
    adapter = FakeRuntimeAdapter()
    profile = adapter.describe_target()

    assert profile.target_id == "TARGET-SYNTHETIC-SANDBOX-001"
    assert profile.target_type == "synthetic_sandbox"
    assert profile.environment == EnvironmentType.SYNTHETIC
    assert profile.observability["model_response"] == ObservabilityState.OBSERVABLE
    assert profile.observability["tool_trace"] == ObservabilityState.OBSERVABLE
    assert profile.observability["runtime_state"] == ObservabilityState.OBSERVABLE
    assert profile.observability["memory_state"] == ObservabilityState.OBSERVABLE
    assert profile.observability["audit_event"] == ObservabilityState.OBSERVABLE


def test_fake_runtime_adapter_initial_and_runtime_observations() -> None:
    adapter = FakeRuntimeAdapter()
    adapter.reset()

    # 1. Initial state
    init_res = adapter.get_initial_state()
    assert init_res.status == ObservationStatus.OBSERVED
    assert "tools_registered" in init_res.value
    assert "search_fake_docs" in init_res.value["tools_registered"]

    # 2. Submit input prompt (safe search)
    submit_res = adapter.submit_input("search synthetic docs", scenario_id="safe_tool_search_allowed")
    assert submit_res.status == ObservationStatus.OBSERVED
    assert submit_res.value["scenario_id"] == "safe_tool_search_allowed"

    # 3. Model response observed
    model_res = adapter.get_model_response()
    assert model_res.status == ObservationStatus.OBSERVED
    assert "search_fake_docs" in model_res.value

    # 4. Tool trace observed
    trace_res = adapter.get_tool_trace()
    assert trace_res.status == ObservationStatus.OBSERVED
    assert len(trace_res.value) > 0
    assert trace_res.value[0]["tool"] == "search_fake_docs"

    # 5. Runtime state observed
    runtime_res = adapter.get_runtime_state()
    assert runtime_res.status == ObservationStatus.OBSERVED
    assert runtime_res.value["scenario_id"] == "safe_tool_search_allowed"
    assert runtime_res.value["blocked"] is False


def test_fake_runtime_adapter_blocked_action_observation() -> None:
    adapter = FakeRuntimeAdapter()
    adapter.reset()

    # Trigger unauthorized secret access scenario
    submit_res = adapter.submit_input("read_fake_secret FAKE_SECRET_DATABASE_PASSWORD")
    assert submit_res.status == ObservationStatus.OBSERVED
    assert submit_res.value["scenario_id"] == "fake_secret_read_blocked"
    assert submit_res.value["blocked"] is True

    runtime_res = adapter.get_runtime_state()
    assert runtime_res.status == ObservationStatus.OBSERVED
    assert runtime_res.value["blocked"] is True
    assert "secret_access_attempt" in runtime_res.value["risk_signals"]


def test_fake_runtime_adapter_deterministic_reset_contract() -> None:
    """Verify deterministic reset contract:

    1. Verify initial baseline is clean
    2. Execute state-mutating memory write
    3. Verify state changed (memory non-empty)
    4. Execute reset()
    5. Verify all declared observable mutable states are restored to baseline.
    """
    adapter = FakeRuntimeAdapter()
    adapter.reset()

    # 1. Verify baseline clean
    mem_init = adapter.get_memory_state()
    assert len(mem_init.value.get("memory_store", [])) == 0

    # 2. Mutate memory and skills state directly via sandbox
    import sandbox.generic_agent_harness.fake_memory as fake_mem
    import sandbox.generic_agent_harness.fake_skill_store as fake_skills
    write_res = fake_mem.write_memory("synthetic test entry", requested_by="tester", approved=True)
    assert write_res["allowed"] is True
    skill_res = fake_skills.create_skill("test_skill", "synthetic test skill", approved=True)
    assert skill_res["allowed"] is True

    # 3. Verify state is mutated
    mem_mutated = adapter.get_memory_state()
    assert len(mem_mutated.value.get("memory_store", [])) == 1
    assert mem_mutated.value["memory_store"][0]["content"] == "synthetic test entry"

    events_mutated = adapter.get_audit_events()
    assert len(events_mutated.value) == 1

    skills_mutated = fake_skills.list_skills()
    assert len(skills_mutated.get("skills", [])) == 1

    # 4. Perform reset
    reset_res = adapter.reset()
    assert reset_res.status == ObservationStatus.OBSERVED
    assert reset_res.value is True

    # 5. Verify all declared observable mutable states are restored to initial baseline
    mem_restored = adapter.get_memory_state()
    assert len(mem_restored.value.get("memory_store", [])) == 0
    assert mem_restored.value.get("event_count", 0) == 0

    events_restored = adapter.get_audit_events()
    assert events_restored.status == ObservationStatus.EMPTY
    assert len(events_restored.value) == 0

    skills_restored = fake_skills.list_skills()
    assert len(skills_restored.get("skills", [])) == 0


def test_fake_runtime_adapter_create_reference_factory() -> None:
    """Verify named factory create_reference() binds the canonical reference profile."""
    adapter = FakeRuntimeAdapter.create_reference()
    profile = adapter.describe_target()
    assert profile.target_id == "TARGET-SYNTHETIC-SANDBOX-001"
    assert profile.environment == EnvironmentType.SYNTHETIC
    assert profile.observability["model_response"] == ObservabilityState.OBSERVABLE

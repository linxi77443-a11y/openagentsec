"""Unit tests for ProtocolTargetAdapter and LegacyBackendResolver (PRD v4.0.2 Phase 2B)."""

from __future__ import annotations

import pytest

from src.openagentsec.models.enums import EnvironmentType, ObservabilityState
from src.openagentsec.models.target_profile import TargetProfile
from src.openagentsec.adapters.backend import (
    BackendUnavailableError,
    FakeBackend,
    LegacyBackendResolver,
)
from src.openagentsec.adapters.config import AdapterConfig
from src.openagentsec.adapters.observation import ObservationStatus
from src.openagentsec.adapters.protocol_adapter import ProtocolTargetAdapter


def _create_test_profile(
    tool_trace_obs: ObservabilityState = ObservabilityState.PARTIALLY_OBSERVABLE,
    runtime_obs: ObservabilityState = ObservabilityState.UNOBSERVABLE,
    memory_obs: ObservabilityState = ObservabilityState.UNOBSERVABLE,
    audit_obs: ObservabilityState = ObservabilityState.UNOBSERVABLE,
) -> TargetProfile:
    return TargetProfile(
        target_id="TARGET-PROTO-TEST-01",
        target_type="openai",
        target_version="1.0.0",
        environment=EnvironmentType.TEST,
        observability={
            "model_response": ObservabilityState.OBSERVABLE,
            "tool_trace": tool_trace_obs,
            "runtime_state": runtime_obs,
            "memory_state": memory_obs,
            "audit_event": audit_obs,
        },
    )


def test_protocol_adapter_model_response_and_unobservable_states() -> None:
    profile = _create_test_profile()
    config = AdapterConfig(endpoint="https://api.example.com/v1")
    fake_backend = FakeBackend(default_response="Simulated AI response")

    adapter = ProtocolTargetAdapter(profile=profile, config=config, backend=fake_backend)

    # 1. Initial response empty
    resp_init = adapter.get_model_response()
    assert resp_init.status == ObservationStatus.EMPTY
    assert resp_init.value is None

    # 2. Submit stimulus
    submit_res = adapter.submit_input("Hello agent")
    assert submit_res.status == ObservationStatus.OBSERVED
    assert submit_res.value["content"] == "Simulated AI response"

    # 3. Model response observed
    resp_obs = adapter.get_model_response()
    assert resp_obs.status == ObservationStatus.OBSERVED
    assert resp_obs.value == "Simulated AI response"

    # 4. Blackbox unobservable states strictly return NOT_OBSERVABLE with value=None
    runtime_res = adapter.get_runtime_state()
    assert runtime_res.status == ObservationStatus.NOT_OBSERVABLE
    assert runtime_res.value is None

    memory_res = adapter.get_memory_state()
    assert memory_res.status == ObservationStatus.NOT_OBSERVABLE
    assert memory_res.value is None

    audit_res = adapter.get_audit_events()
    assert audit_res.status == ObservationStatus.NOT_OBSERVABLE
    assert audit_res.value is None


def test_protocol_adapter_tool_trace_intent_vs_natural_language() -> None:
    """Verify structured tool_calls result in PARTIAL, and natural-language text is NOT treated as tool trace."""
    profile = _create_test_profile(tool_trace_obs=ObservabilityState.PARTIALLY_OBSERVABLE)
    config = AdapterConfig(endpoint="https://api.example.com/v1")

    # Case A: Structured tool call present
    backend_with_tool = FakeBackend(
        default_response="Calling search tool",
        tool_calls=[{"id": "call_1", "name": "search_docs", "arguments": {"q": "policy"}}],
    )
    adapter_tool = ProtocolTargetAdapter(profile=profile, config=config, backend=backend_with_tool)
    adapter_tool.submit_input("Find policy")

    trace_res = adapter_tool.get_tool_trace()
    assert trace_res.status == ObservationStatus.PARTIAL
    assert trace_res.observability == ObservabilityState.PARTIALLY_OBSERVABLE
    assert len(trace_res.value) == 1
    assert trace_res.value[0]["name"] == "search_docs"
    assert "intent only" in trace_res.reason

    # Case B: Natural language "thought" text only — NEVER treated as tool trace
    backend_with_thought = FakeBackend(
        default_response="Thought: I should search docs. Result: None.",
        tool_calls=[],
    )
    adapter_thought = ProtocolTargetAdapter(profile=profile, config=config, backend=backend_with_thought)
    adapter_thought.submit_input("Find policy")

    thought_trace_res = adapter_thought.get_tool_trace()
    assert thought_trace_res.status == ObservationStatus.EMPTY
    assert thought_trace_res.value == []


def test_protocol_adapter_unobservable_tool_trace() -> None:
    """When TargetProfile declares tool_trace as unobservable, get_tool_trace() returns NOT_OBSERVABLE."""
    profile = _create_test_profile(tool_trace_obs=ObservabilityState.UNOBSERVABLE)
    config = AdapterConfig(endpoint="https://api.example.com/v1")
    backend = FakeBackend(default_response="Response", tool_calls=[{"name": "tool_x"}])

    adapter = ProtocolTargetAdapter(profile=profile, config=config, backend=backend)
    adapter.submit_input("Test")

    trace_res = adapter.get_tool_trace()
    assert trace_res.status == ObservationStatus.NOT_OBSERVABLE
    assert trace_res.observability == ObservabilityState.UNOBSERVABLE
    assert trace_res.value is None


def test_protocol_adapter_reset_is_partial() -> None:
    """Protocol adapter reset only resets local conversation history and reports PARTIAL."""
    profile = _create_test_profile()
    config = AdapterConfig(endpoint="https://api.example.com/v1")
    backend = FakeBackend(default_response="Response")

    adapter = ProtocolTargetAdapter(profile=profile, config=config, backend=backend)
    adapter.submit_input("Turn 1")
    assert len(backend.get_history()) == 2

    reset_res = adapter.reset()
    assert reset_res.status == ObservationStatus.PARTIAL
    assert reset_res.value is True
    assert "Local conversation history reset only" in reset_res.reason
    assert len(backend.get_history()) == 0


def test_legacy_backend_resolver_missing_module_fails_closed() -> None:
    """LegacyBackendResolver fails closed with BackendUnavailableError when module is unavailable."""
    with pytest.raises(BackendUnavailableError, match="unavailable in current environment"):
        LegacyBackendResolver.resolve_fake_harness_module  # Callable check
        # Simulate import failure
        import importlib
        orig_import = importlib.import_module
        def mock_failing_import(name, *args, **kwargs):
            if "sandbox.generic_agent_harness" in name:
                raise ModuleNotFoundError(f"No module named '{name}'")
            return orig_import(name, *args, **kwargs)

        import unittest.mock as mock
        with mock.patch("importlib.import_module", side_effect=mock_failing_import):
            LegacyBackendResolver.resolve_fake_harness_module()

"""Unit tests for TargetAdapter Contract completeness and boundary isolation (PRD v4.0.2 Phase 2B)."""

from __future__ import annotations

import inspect
import pytest

from src.openagentsec.models.enums import EnvironmentType, ObservabilityState
from src.openagentsec.models.target_profile import TargetProfile
from src.openagentsec.adapters.base import TargetAdapter
from src.openagentsec.adapters.config import AdapterConfig
from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus


def test_target_adapter_contract_method_completeness() -> None:
    """Verify TargetAdapter declares all 9 statutory PRD v4.0.2 §7.3 methods."""
    required_methods = {
        "describe_target",
        "get_initial_state",
        "submit_input",
        "get_model_response",
        "get_tool_trace",
        "get_runtime_state",
        "get_memory_state",
        "get_audit_events",
        "reset",
    }
    adapter_methods = {
        name for name, _ in inspect.getmembers(TargetAdapter, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    missing = required_methods - adapter_methods
    assert not missing, f"TargetAdapter must declare all 9 methods. Missing: {missing}"


def test_describe_target_returns_immutable_clean_profile() -> None:
    """describe_target() must return original TargetProfile without endpoint or secret pollution."""
    profile = TargetProfile(
        target_id="TARGET-TEST-01",
        target_type="custom_agent",
        target_version="1.0.0",
        environment=EnvironmentType.TEST,
        identities=["user_01"],
        tenants=["tenant_01"],
        observability={"model_response": ObservabilityState.OBSERVABLE},
    )
    config = AdapterConfig(
        endpoint="https://api.example.com/v1",
        credential_ref="ENV:TEST_KEY",
    )

    class MinimalAdapter(TargetAdapter):
        def get_initial_state(self): pass
        def submit_input(self, stimulus, **kwargs): pass
        def get_model_response(self): pass
        def get_tool_trace(self): pass
        def get_runtime_state(self): pass
        def get_memory_state(self): pass
        def get_audit_events(self): pass
        def reset(self): pass

    adapter = MinimalAdapter(profile=profile, config=config)
    described = adapter.describe_target()

    assert described.target_id == "TARGET-TEST-01"
    assert described.target_type == "custom_agent"
    assert described.environment == EnvironmentType.TEST

    # Verify no endpoint or credential parameters leaked into profile
    assert not hasattr(described, "endpoint")
    assert not hasattr(described, "credential_ref")
    assert "https://api.example.com/v1" not in str(described.to_dict())

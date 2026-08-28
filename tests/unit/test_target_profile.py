"""Unit tests for TargetProfile model, schema, loader, and validator (PRD v4.0.2 §7 / Phase 1B)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.openagentsec.models import (
    EnvironmentType,
    ObservabilityState,
    ProductionFixtureError,
    ProhibitedCredentialError,
    SchemaValidationError,
    TargetProfile,
    load_target_profile,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "v4" / "target_profile"


def test_valid_synthetic_target() -> None:
    """Verify valid synthetic TargetProfile loads and binds correctly."""
    fixture_path = FIXTURES_DIR / "valid_synthetic.yaml"
    target = load_target_profile(fixture_path)

    assert isinstance(target, TargetProfile)
    assert target.target_id == "TARGET-SYNTHETIC-FINANCE-01"
    assert target.target_type == "synthetic_agent_v2"
    assert target.environment == EnvironmentType.SYNTHETIC
    assert target.observability["model_response"] == ObservabilityState.OBSERVABLE
    assert target.observability["memory_state"] == ObservabilityState.UNOBSERVABLE
    assert target.observability["audit_event"] == ObservabilityState.PARTIALLY_OBSERVABLE

    d = target.to_dict()
    assert d["target_id"] == "TARGET-SYNTHETIC-FINANCE-01"
    assert d["environment"] == "synthetic"
    assert d["observability"]["tool_trace"] == "observable"


def test_valid_staging_target() -> None:
    """Verify valid staging TargetProfile loads correctly."""
    fixture_path = FIXTURES_DIR / "valid_staging.yaml"
    target = load_target_profile(fixture_path)

    assert target.target_id == "TARGET-STAGING-CHATBOT-02"
    assert target.target_type == "dify"
    assert target.environment == EnvironmentType.STAGING


def test_open_string_target_type() -> None:
    """Verify target_type accepts any valid machine-readable string pattern without closed enum."""
    raw = {
        "target_id": "TARGET-CUSTOM-01",
        "target_type": "custom_agent_langgraph_v3",
        "target_version": "3.2.1",
        "environment": "test",
        "identities": [], "tenants": [], "roles": [], "tools": [],
        "resources": [], "rag_sources": [], "memory_stores": [],
        "approval_points": [], "connectors": [], "runtime_capabilities": [],
        "output_channels": [],
        "observability": {},
    }
    target = load_target_profile(raw)
    assert target.target_type == "custom_agent_langgraph_v3"


def test_missing_target_id_rejected() -> None:
    """Verify missing target_id fails schema validation."""
    fixture_path = FIXTURES_DIR / "missing_target_id.yaml"
    with pytest.raises(SchemaValidationError) as exc_info:
        load_target_profile(fixture_path)
    assert "target_id" in str(exc_info.value)


def test_invalid_observability_state_rejected() -> None:
    """Verify observability values outside (observable, unobservable, partially_observable) are rejected."""
    fixture_path = FIXTURES_DIR / "invalid_observability_state.yaml"
    with pytest.raises(SchemaValidationError) as exc_info:
        load_target_profile(fixture_path)
    assert "observability" in str(exc_info.value)


def test_missing_observability_remains_absent_never_autofilled() -> None:
    """Verify undeclared observability channels stay absent and are never auto-filled or guessed."""
    fixture_path = FIXTURES_DIR / "undeclared_observability_intact.yaml"
    target = load_target_profile(fixture_path)

    # Declared entries must exist
    assert "model_response" in target.observability
    assert "tool_trace" in target.observability

    # Undeclared entries must NOT exist or be auto-filled to unobservable
    assert "audit_events" not in target.observability
    assert "memory_state" not in target.observability
    assert "network_traffic" not in target.observability
    assert len(target.observability) == 2


def test_prohibited_secret_rejected() -> None:
    """Verify connection secrets and api tokens are strictly rejected."""
    fixture_path = FIXTURES_DIR / "prohibited_secret.yaml"
    with pytest.raises((ProhibitedCredentialError, SchemaValidationError)) as exc_info:
        load_target_profile(fixture_path)
    assert "api_token" in str(exc_info.value).lower() or "additionalproperties" in str(exc_info.value).lower()


def test_production_fixture_rejected() -> None:
    """Verify production target is rejected when loaded in fixture mode (is_fixture=True)."""
    fixture_path = FIXTURES_DIR / "production_fixture_rejected.yaml"
    with pytest.raises(ProductionFixtureError) as exc_info:
        load_target_profile(fixture_path, is_fixture=True)
    assert "Production target 'TARGET-PROD-LIVE-001' cannot be loaded in fixture mode" in str(exc_info.value)


def test_production_target_allowed_in_non_fixture_mode() -> None:
    """Verify production target can still be described by TargetProfile in governance context."""
    fixture_path = FIXTURES_DIR / "production_fixture_rejected.yaml"
    target = load_target_profile(fixture_path, is_fixture=False)
    assert target.environment == EnvironmentType.PRODUCTION

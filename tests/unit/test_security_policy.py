"""Unit tests for SecurityPolicy model, schema, loader, and validator (PRD v4.0.2 §5 / Phase 1B)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.openagentsec.models import (
    ConflictPermissionError,
    DuplicateKeyError,
    PolicyApproval,
    PolicyInvariant,
    PolicyPermissions,
    ProhibitedCredentialError,
    SchemaValidationError,
    SecurityPolicy,
    SemanticValidationError,
    Severity,
    load_json_str,
    load_security_policy,
    load_yaml_str,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "v4" / "security_policy"


def test_valid_minimal_policy() -> None:
    """Verify minimal valid SecurityPolicy loads successfully."""
    fixture_path = FIXTURES_DIR / "valid_minimal.yaml"
    policy = load_security_policy(fixture_path)

    assert isinstance(policy, SecurityPolicy)
    assert policy.policy_id == "POL-MIN-001"
    assert policy.version == "1.0.0"
    assert policy.target_refs == ["TARGET-AGENT-01"]
    assert isinstance(policy.allowed, PolicyPermissions)
    assert isinstance(policy.denied, PolicyPermissions)
    assert policy.invariants == []
    assert policy.approvals == []

    d = policy.to_dict()
    assert d["policy_id"] == "POL-MIN-001"
    assert d["allowed"]["tools"] == []


def test_valid_full_policy() -> None:
    """Verify full enterprise SecurityPolicy with invariants and approvals."""
    fixture_path = FIXTURES_DIR / "valid_full.yaml"
    policy = load_security_policy(fixture_path)

    assert policy.policy_id == "POL-ENTERPRISE-001"
    assert len(policy.invariants) == 2
    assert policy.invariants[0].invariant_id == "INV-TENANT-001"
    assert policy.invariants[0].severity == Severity.CRITICAL
    assert policy.invariants[1].severity == Severity.HIGH

    assert len(policy.approvals) == 1
    assert policy.approvals[0].action == "export_quarterly_audit_report"
    assert policy.approvals[0].required is True
    assert policy.approvals[0].approver == "secops_manager"

    assert "execute_fund_transfer" in policy.denied.tools
    assert "query_balance" in policy.allowed.tools


def test_invalid_severity_rejected() -> None:
    """Verify non-enum severity fails schema validation (fail-closed, not model generated)."""
    fixture_path = FIXTURES_DIR / "invalid_severity.yaml"
    with pytest.raises(SchemaValidationError) as exc_info:
        load_security_policy(fixture_path)
    assert "severity" in str(exc_info.value).lower()


def test_duplicate_invariant_id_rejected() -> None:
    """Verify duplicate invariant_id across policy invariants is rejected."""
    fixture_path = FIXTURES_DIR / "duplicate_invariant_id.yaml"
    with pytest.raises(SemanticValidationError) as exc_info:
        load_security_policy(fixture_path)
    assert "Duplicate invariant_id" in str(exc_info.value)


def test_duplicate_yaml_key_rejected() -> None:
    """Verify duplicate keys in YAML mappings raise DuplicateKeyError."""
    fixture_path = FIXTURES_DIR / "duplicate_yaml_key.yaml"
    with pytest.raises(DuplicateKeyError) as exc_info:
        load_security_policy(fixture_path)
    assert "Duplicate YAML key 'tools'" in str(exc_info.value)


def test_duplicate_json_key_rejected() -> None:
    """Verify duplicate keys in JSON objects raise DuplicateKeyError."""
    json_str = '{"policy_id": "POL-1", "policy_id": "POL-2"}'
    with pytest.raises(DuplicateKeyError) as exc_info:
        load_json_str(json_str)
    assert "Duplicate JSON key 'policy_id'" in str(exc_info.value)


def test_allowed_denied_conflict_rejected() -> None:
    """Verify direct permission conflict between allowed and denied raises ConflictPermissionError."""
    fixture_path = FIXTURES_DIR / "allowed_denied_conflict.yaml"
    with pytest.raises(ConflictPermissionError) as exc_info:
        load_security_policy(fixture_path)
    assert "export_financial_report" in str(exc_info.value)


def test_missing_policy_id_rejected() -> None:
    """Verify missing required policy_id fails schema validation."""
    fixture_path = FIXTURES_DIR / "missing_policy_id.yaml"
    with pytest.raises(SchemaValidationError) as exc_info:
        load_security_policy(fixture_path)
    assert "policy_id" in str(exc_info.value)


def test_prohibited_credential_field_rejected() -> None:
    """Verify credential fields like api_key are strictly rejected."""
    fixture_path = FIXTURES_DIR / "prohibited_credential.yaml"
    with pytest.raises((ProhibitedCredentialError, SchemaValidationError)) as exc_info:
        load_security_policy(fixture_path)
    assert "api_key" in str(exc_info.value).lower() or "credential" in str(exc_info.value).lower()


def test_invalid_approval_rejected() -> None:
    """Verify approval with empty approver is rejected."""
    fixture_path = FIXTURES_DIR / "invalid_approval.yaml"
    with pytest.raises((SchemaValidationError, SemanticValidationError)):
        load_security_policy(fixture_path)


def test_duplicate_approval_action_rejected() -> None:
    """Verify duplicate approval action in approvals array is rejected."""
    raw = {
        "policy_id": "POL-DUP-APP-001",
        "version": "1.0.0",
        "target_refs": ["TARGET-01"],
        "allowed": {
            "identities": [], "tools": [], "actions": [], "resources": [],
            "scopes": [], "outputs": [], "delegation": [], "persistent_state": []
        },
        "denied": {
            "identities": [], "tools": [], "actions": [], "resources": [],
            "scopes": [], "outputs": [], "delegation": [], "persistent_state": []
        },
        "approvals": [
            {"action": "export_report", "required": True, "approver": "alice"},
            {"action": "export_report", "required": False, "approver": "bob"},
        ],
        "invariants": [],
        "critical_actions": [],
        "evidence_requirements": [],
    }
    with pytest.raises(SemanticValidationError) as exc_info:
        load_security_policy(raw)
    assert "Duplicate approval action" in str(exc_info.value)


def test_recursive_additional_properties_rejected() -> None:
    """Verify unknown keys in sub-objects (e.g. allowed, invariants) are rejected by schema."""
    raw = {
        "policy_id": "POL-EXTRA-001",
        "version": "1.0.0",
        "target_refs": ["TARGET-01"],
        "allowed": {
            "identities": [], "tools": [], "actions": [], "resources": [],
            "scopes": [], "outputs": [], "delegation": [], "persistent_state": [],
            "unknown_permission_category": ["extra"],
        },
        "denied": {
            "identities": [], "tools": [], "actions": [], "resources": [],
            "scopes": [], "outputs": [], "delegation": [], "persistent_state": []
        },
        "approvals": [],
        "invariants": [],
        "critical_actions": [],
        "evidence_requirements": [],
    }
    with pytest.raises(SchemaValidationError) as exc_info:
        load_security_policy(raw)
    assert "additionalProperties" in str(exc_info.value) or "unknown_permission_category" in str(exc_info.value)

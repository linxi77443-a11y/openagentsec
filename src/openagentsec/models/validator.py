"""Validation engine and schema-model binding for OpenAgentSec.

Layered architecture:
1. JSON Schema Validation (Structural source of truth: fields, types, required, enum, range, recursive additionalProperties: false)
2. Dataclass Binding (Typed object representation, serialization)
3. Semantic Validation (Cross-field invariants, uniqueness, allowed/denied conflicts, fixture mode guards)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Set, Union

import jsonschema
import yaml

from .enums import EnvironmentType, MaturityLevel, ObservabilityState, PlannerMode, Severity
from .evaluation_objective import MAX_OBJECTIVE_RUNS, MAX_OBJECTIVE_STEPS, EvaluationObjective
from .exceptions import (
    ConflictPermissionError,
    ForbiddenScenarioFieldError,
    ProductionFixtureError,
    ProhibitedCredentialError,
    SchemaValidationError,
    SemanticValidationError,
)
from .loader import load_raw_data
from .security_policy import (
    PolicyApproval,
    PolicyInvariant,
    PolicyPermissions,
    SecurityPolicy,
)
from .target_profile import TargetProfile

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas" / "v4"

FORBIDDEN_SCENARIO_FIELDS: Set[str] = {
    "scenario_steps",
    "payloads",
    "concrete_steps",
    "execution_sequence",
    "attack_chain",
    "exploit_steps",
}

PROHIBITED_CREDENTIAL_KEYS: Set[str] = {
    "api_key",
    "apikey",
    "api_token",
    "token",
    "secret",
    "password",
    "passwd",
    "private_key",
    "credential",
    "credentials",
    "auth_token",
    "bearer_token",
    "access_token",
}


@lru_cache(maxsize=8)
def get_schema(schema_name: str) -> Dict[str, Any]:
    """Load and cache JSON Schema YAML file."""
    schema_path = SCHEMAS_DIR / f"{schema_name}.schema.yaml"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
    return yaml.safe_load(schema_path.read_text(encoding="utf-8"))


def _scan_for_prohibited_credentials(data: Any, path: str = "") -> None:
    """Recursively scan mapping keys and string values for prohibited credentials."""
    if isinstance(data, dict):
        for k, v in data.items():
            k_lower = str(k).lower().strip()
            if any(cred_key in k_lower for cred_key in PROHIBITED_CREDENTIAL_KEYS):
                raise ProhibitedCredentialError(
                    f"Prohibited credential field '{k}' detected at '{path or 'root'}'. "
                    "Credentials and secrets must never be stored in governance policies or target profiles."
                )
            _scan_for_prohibited_credentials(v, f"{path}.{k}" if path else str(k))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            _scan_for_prohibited_credentials(item, f"{path}[{idx}]")
    elif isinstance(data, str):
        val_lower = data.lower().strip()
        # Detect clear secret assignments like "api_key=sk-..." or "Bearer eyJ..."
        if any(prefix in val_lower for prefix in ("bearer eyj", "sk-live-", "ghp_", "xoxb-")):
            raise ProhibitedCredentialError(
                f"Prohibited raw credential pattern detected in value at '{path}'. "
                "Credentials and secrets must never be stored in governance policies or target profiles."
            )


def validate_schema(data: Dict[str, Any], schema_name: str) -> None:
    """Validate raw dictionary against the specified JSON schema draft-7."""
    schema = get_schema(schema_name)
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    if errors:
        error_msgs = []
        is_scenario_violation = False
        for err in errors:
            msg = f"Path '{'.'.join(str(p) for p in err.path)}': {err.message}"
            error_msgs.append(msg)
            # Check if an additionalProperties failure was caused by a scenario field
            if "additionalProperties" in err.message or any(f in str(err.message) for f in FORBIDDEN_SCENARIO_FIELDS):
                is_scenario_violation = True

        combined_msg = f"JSON Schema validation failed for {schema_name}:\n" + "\n".join(f" - {m}" for m in error_msgs)
        if is_scenario_violation:
            raise ForbiddenScenarioFieldError(combined_msg, errors=error_msgs)
        raise SchemaValidationError(combined_msg, errors=error_msgs)


def bind_security_policy(raw: Dict[str, Any]) -> SecurityPolicy:
    """Bind validated dictionary to SecurityPolicy dataclass."""
    allowed_data = raw.get("allowed", {})
    denied_data = raw.get("denied", {})

    allowed = PolicyPermissions(
        identities=list(allowed_data.get("identities", [])),
        tools=list(allowed_data.get("tools", [])),
        actions=list(allowed_data.get("actions", [])),
        resources=list(allowed_data.get("resources", [])),
        scopes=list(allowed_data.get("scopes", [])),
        outputs=list(allowed_data.get("outputs", [])),
        delegation=list(allowed_data.get("delegation", [])),
        persistent_state=list(allowed_data.get("persistent_state", [])),
    )
    denied = PolicyPermissions(
        identities=list(denied_data.get("identities", [])),
        tools=list(denied_data.get("tools", [])),
        actions=list(denied_data.get("actions", [])),
        resources=list(denied_data.get("resources", [])),
        scopes=list(denied_data.get("scopes", [])),
        outputs=list(denied_data.get("outputs", [])),
        delegation=list(denied_data.get("delegation", [])),
        persistent_state=list(denied_data.get("persistent_state", [])),
    )

    approvals = [
        PolicyApproval(
            action=a["action"],
            required=bool(a["required"]),
            approver=str(a["approver"]),
        )
        for a in raw.get("approvals", [])
    ]

    invariants = [
        PolicyInvariant(
            invariant_id=i["invariant_id"],
            statement=i["statement"],
            severity=Severity(i["severity"]),
            rationale=i["rationale"],
            retest_policy_ref=i.get("retest_policy_ref"),
        )
        for i in raw.get("invariants", [])
    ]

    return SecurityPolicy(
        policy_id=raw["policy_id"],
        version=raw["version"],
        target_refs=list(raw["target_refs"]),
        allowed=allowed,
        denied=denied,
        approvals=approvals,
        invariants=invariants,
        critical_actions=list(raw.get("critical_actions", [])),
        evidence_requirements=list(raw.get("evidence_requirements", [])),
    )


def validate_security_policy_semantics(policy: SecurityPolicy, raw: Dict[str, Any]) -> None:
    """Perform cross-field semantic validation on SecurityPolicy."""
    # 1. Prohibited credentials check
    _scan_for_prohibited_credentials(raw)

    # 2. Invariant ID uniqueness
    seen_ids: Set[str] = set()
    for inv in policy.invariants:
        if inv.invariant_id in seen_ids:
            raise SemanticValidationError(
                f"Duplicate invariant_id '{inv.invariant_id}' in policy '{policy.policy_id}'. "
                "All policy invariants must have globally unique IDs within the policy."
            )
        seen_ids.add(inv.invariant_id)

    # 3. Direct Allowed vs Denied conflict check
    dimensions = (
        ("identities", policy.allowed.identities, policy.denied.identities),
        ("tools", policy.allowed.tools, policy.denied.tools),
        ("actions", policy.allowed.actions, policy.denied.actions),
        ("resources", policy.allowed.resources, policy.denied.resources),
        ("scopes", policy.allowed.scopes, policy.denied.scopes),
        ("outputs", policy.allowed.outputs, policy.denied.outputs),
        ("delegation", policy.allowed.delegation, policy.denied.delegation),
        ("persistent_state", policy.allowed.persistent_state, policy.denied.persistent_state),
    )
    for dim_name, allowed_items, denied_items in dimensions:
        conflict = set(allowed_items) & set(denied_items)
        if conflict:
            raise ConflictPermissionError(
                f"Direct permission conflict in '{dim_name}': {sorted(conflict)} is present in both allowed and denied."
            )

    # 4. Approval action uniqueness and approver requirement
    seen_actions: Set[str] = set()
    for app in policy.approvals:
        if app.action in seen_actions:
            raise SemanticValidationError(
                f"Duplicate approval action '{app.action}' found in approvals."
            )
        seen_actions.add(app.action)
        if app.required and not app.approver.strip():
            raise SemanticValidationError(
                f"Approval for action '{app.action}' is required but approver is empty."
            )


def load_security_policy(source: Union[str, Path, Dict[str, Any]]) -> SecurityPolicy:
    """Load, structurally validate against JSON schema, bind to dataclass, and validate semantics."""
    raw = load_raw_data(source)
    validate_schema(raw, "security_policy")
    policy = bind_security_policy(raw)
    validate_security_policy_semantics(policy, raw)
    return policy


def bind_evaluation_objective(raw: Dict[str, Any]) -> EvaluationObjective:
    """Bind validated dictionary to EvaluationObjective dataclass."""
    return EvaluationObjective(
        objective_id=raw["objective_id"],
        risk_refs=list(raw["risk_refs"]),
        policy_refs=list(raw["policy_refs"]),
        target_refs=list(raw["target_refs"]),
        evaluation_question=raw["evaluation_question"],
        target_behavior=raw["target_behavior"],
        undesired_behavior=raw["undesired_behavior"],
        required_observations=list(raw["required_observations"]),
        required_evidence=list(raw["required_evidence"]),
        permitted_stimulus_types=list(raw["permitted_stimulus_types"]),
        planner_mode=PlannerMode(raw["planner_mode"]),
        maturity_required=MaturityLevel(raw["maturity_required"]),
        max_steps=int(raw["max_steps"]),
        max_runs=int(raw["max_runs"]),
        stop_conditions=list(raw.get("stop_conditions", [])),
        safety_constraints=list(raw.get("safety_constraints", [])),
        title=raw.get("title"),
    )


def validate_evaluation_objective_semantics(objective: EvaluationObjective, raw: Dict[str, Any]) -> None:
    """Perform semantic validation on EvaluationObjective."""
    # JSON schema already validates structural bounds and rejects forbidden fields.
    # Validate safety constraints are not empty strings if list provided
    for sc in objective.safety_constraints:
        if not sc.strip():
            raise SemanticValidationError("Empty string in safety_constraints is not allowed.")


def load_evaluation_objective(source: Union[str, Path, Dict[str, Any]]) -> EvaluationObjective:
    """Load, structurally validate against JSON schema, bind to dataclass, and validate semantics."""
    raw = load_raw_data(source)
    validate_schema(raw, "evaluation_objective")
    obj = bind_evaluation_objective(raw)
    validate_evaluation_objective_semantics(obj, raw)
    return obj


def bind_target_profile(raw: Dict[str, Any]) -> TargetProfile:
    """Bind validated dictionary to TargetProfile dataclass."""
    observability_raw = raw.get("observability", {})
    observability_map = {
        k: ObservabilityState(v) for k, v in observability_raw.items()
    }

    return TargetProfile(
        target_id=raw["target_id"],
        target_type=raw["target_type"],
        target_version=raw["target_version"],
        environment=EnvironmentType(raw["environment"]),
        identities=list(raw.get("identities", [])),
        tenants=list(raw.get("tenants", [])),
        roles=list(raw.get("roles", [])),
        tools=list(raw.get("tools", [])),
        resources=list(raw.get("resources", [])),
        rag_sources=list(raw.get("rag_sources", [])),
        memory_stores=list(raw.get("memory_stores", [])),
        approval_points=list(raw.get("approval_points", [])),
        connectors=list(raw.get("connectors", [])),
        runtime_capabilities=list(raw.get("runtime_capabilities", [])),
        output_channels=list(raw.get("output_channels", [])),
        observability=observability_map,
    )


def validate_target_profile_semantics(
    target: TargetProfile, raw: Dict[str, Any], is_fixture: bool = False
) -> None:
    """Perform cross-field semantic validation on TargetProfile."""
    # 1. Prohibited credentials check
    _scan_for_prohibited_credentials(raw)

    # 2. Fixture mode safety check: reject production targets as test fixtures
    if is_fixture and target.environment == EnvironmentType.PRODUCTION:
        raise ProductionFixtureError(
            f"Production target '{target.target_id}' cannot be loaded in fixture mode. "
            "Test fixtures must use synthetic, test, or staging target environments."
        )


def load_target_profile(
    source: Union[str, Path, Dict[str, Any]], is_fixture: bool = False
) -> TargetProfile:
    """Load, structurally validate against JSON schema, bind to dataclass, and validate semantics."""
    raw = load_raw_data(source)
    validate_schema(raw, "target_profile")
    profile = bind_target_profile(raw)
    validate_target_profile_semantics(profile, raw, is_fixture=is_fixture)
    return profile

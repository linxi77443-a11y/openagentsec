"""OpenAgentSec Phase 1B Core Evaluation Models & Schemas.

PRD v4.0.2 Phase 1B:
- SecurityPolicy: Governance Plane declarative policy
- EvaluationObjective: Evaluation Plane objective definition
- TargetProfile: Target security properties and explicit observability
"""

from __future__ import annotations

from .enums import (
    EnvironmentType,
    MaturityLevel,
    ObservabilityState,
    PlannerMode,
    Severity,
)
from .evaluation_objective import (
    MAX_OBJECTIVE_RUNS,
    MAX_OBJECTIVE_STEPS,
    EvaluationObjective,
)
from .exceptions import (
    ConflictPermissionError,
    DuplicateKeyError,
    ForbiddenScenarioFieldError,
    OpenAgentSecModelError,
    ProductionFixtureError,
    ProhibitedCredentialError,
    SchemaValidationError,
    SemanticValidationError,
    SerializationLoadError,
)
from .loader import (
    load_json_str,
    load_raw_data,
    load_yaml_str,
)
from .security_policy import (
    PolicyApproval,
    PolicyInvariant,
    PolicyPermissions,
    SecurityPolicy,
)
from .target_profile import TargetProfile
from .validator import (
    bind_evaluation_objective,
    bind_security_policy,
    bind_target_profile,
    get_schema,
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
    validate_evaluation_objective_semantics,
    validate_schema,
    validate_security_policy_semantics,
    validate_target_profile_semantics,
)

__all__ = [
    # Enums
    "Severity",
    "PlannerMode",
    "ObservabilityState",
    "MaturityLevel",
    "EnvironmentType",
    # Constants
    "MAX_OBJECTIVE_STEPS",
    "MAX_OBJECTIVE_RUNS",
    # Dataclasses
    "SecurityPolicy",
    "PolicyPermissions",
    "PolicyApproval",
    "PolicyInvariant",
    "EvaluationObjective",
    "TargetProfile",
    # Loaders & Validators
    "load_security_policy",
    "load_evaluation_objective",
    "load_target_profile",
    "load_raw_data",
    "load_yaml_str",
    "load_json_str",
    "get_schema",
    "validate_schema",
    "bind_security_policy",
    "bind_evaluation_objective",
    "bind_target_profile",
    "validate_security_policy_semantics",
    "validate_evaluation_objective_semantics",
    "validate_target_profile_semantics",
    # Exceptions
    "OpenAgentSecModelError",
    "DuplicateKeyError",
    "SerializationLoadError",
    "SchemaValidationError",
    "SemanticValidationError",
    "ProhibitedCredentialError",
    "ConflictPermissionError",
    "ProductionFixtureError",
    "ForbiddenScenarioFieldError",
]

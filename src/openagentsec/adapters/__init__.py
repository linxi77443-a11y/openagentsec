"""OpenAgentSec Target Adapters Module (PRD v4.0.2 Phase 2B).

Provides canonical TargetAdapter Contract, ObservationResult semantics,
AdapterConfig credential safeguards, and thin backend wrapper convergence.
"""

from .backend import (
    BackendUnavailableError,
    FakeBackend,
    LegacyBackendResolver,
    LegacyBackendWrapper,
    TargetBackend,
)
from .base import TargetAdapter
from .config import (
    AdapterConfig,
    AdapterConfigurationError,
    CredentialResolver,
    EnvCredentialResolver,
)
from .fake_runtime_adapter import FakeRuntimeAdapter
from .observation import (
    ObservationResult,
    ObservationSemanticError,
    ObservationStatus,
)
from .protocol_adapter import ProtocolTargetAdapter

__all__ = [
    "TargetAdapter",
    "ObservationResult",
    "ObservationStatus",
    "ObservationSemanticError",
    "AdapterConfig",
    "AdapterConfigurationError",
    "CredentialResolver",
    "EnvCredentialResolver",
    "TargetBackend",
    "FakeBackend",
    "LegacyBackendResolver",
    "LegacyBackendWrapper",
    "BackendUnavailableError",
    "ProtocolTargetAdapter",
    "FakeRuntimeAdapter",
]

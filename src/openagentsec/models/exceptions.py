"""Exception classes for OpenAgentSec governance and evaluation models."""

from __future__ import annotations


class OpenAgentSecModelError(Exception):
    """Base error for all model, schema, loading, and validation failures."""


class DuplicateKeyError(OpenAgentSecModelError):
    """Raised when a YAML or JSON document contains duplicate mapping keys."""


class SerializationLoadError(OpenAgentSecModelError):
    """Raised when loading or parsing YAML/JSON content fails."""


class SchemaValidationError(OpenAgentSecModelError):
    """Raised when JSON schema validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or [message]


class SemanticValidationError(OpenAgentSecModelError):
    """Raised when cross-field semantic validation fails."""


class ProhibitedCredentialError(SemanticValidationError):
    """Raised when credentials, secrets, or raw keys are detected in models."""


class ConflictPermissionError(SemanticValidationError):
    """Raised when direct conflicts exist between allowed and denied permissions."""


class ProductionFixtureError(SemanticValidationError):
    """Raised when a production environment profile is loaded in fixture mode."""


class ForbiddenScenarioFieldError(SchemaValidationError):
    """Raised when concrete scenario or exploit execution fields are present in objectives."""

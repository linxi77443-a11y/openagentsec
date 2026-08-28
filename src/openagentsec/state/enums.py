"""State dimension and change enumeration types for OpenAgentSec (PRD v4.0.2 §8.2 & §12.2)."""

from __future__ import annotations

from enum import Enum


class StateDimension(str, Enum):
    """PRD v4.0.2 §8.2 statutory 10 agent security state dimensions."""
    IDENTITY = "identity"
    GOAL = "goal"
    TRUST = "trust"
    CONTEXT = "context"
    RESOURCE = "resource"
    TOOL = "tool"
    MEMORY = "memory"
    APPROVAL = "approval"
    CONTROL = "control"
    ENVIRONMENT = "environment"


class ChangeStatus(str, Enum):
    """State transition delta change status (PRD v4.0.2 §12.2)."""
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    INDETERMINATE = "indeterminate"

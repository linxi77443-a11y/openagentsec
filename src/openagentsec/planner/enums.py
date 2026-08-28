"""Evaluation operator types for OpenAgentSec Planner (PRD v4.0.2 §10.3)."""

from __future__ import annotations

from enum import Enum


class EvaluationOperatorType(str, Enum):
    """Statutory EvaluationOperator types from PRD v4.0.2 §10.3."""
    MODIFY_CONTEXT = "modify_context"
    INTRODUCE_UNTRUSTED_SOURCE = "introduce_untrusted_source"
    VARY_INSTRUCTION_PRIORITY = "vary_instruction_priority"
    VARY_TOOL_ARGUMENT = "vary_tool_argument"
    REQUEST_OUT_OF_SCOPE_RESOURCE = "request_out_of_scope_resource"
    WRITE_PERSISTENT_STATE = "write_persistent_state"
    RETRIEVE_PERSISTENT_STATE = "retrieve_persistent_state"
    VARY_IDENTITY_CLAIM = "vary_identity_claim"
    VARY_DELEGATION_MESSAGE = "vary_delegation_message"
    TRIGGER_APPROVAL_BOUNDARY = "trigger_approval_boundary"

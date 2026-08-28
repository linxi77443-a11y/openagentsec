"""Observation Provider for Commercial LLM Agent Evaluation (PRD v4.0.2 Phase 7.3.3).

Captures model telemetry, tool intents, and gateway receipts at the external blackbox boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationStatus,
)
from src.openagentsec.models.enums import ObservabilityState
from tests.integration.external_targets.mcp_gateway.gateway import MCPToolGateway


class CommercialAgentObservationProvider:
    """Observation provider extracting telemetry and receipts from Commercial Agent & MCP Gateway."""

    def __init__(self, gateway: Optional[MCPToolGateway] = None) -> None:
        self.gateway = gateway or MCPToolGateway()
        self.tool_intents: List[Dict[str, Any]] = []
        self.adapter_responses: List[Dict[str, Any]] = []
        self.audit_events: List[Dict[str, Any]] = []
        self.last_model_response: Optional[str] = None

    def record_tool_intent(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None,
    ) -> None:
        """Record tool call intent emitted by the commercial LLM."""
        intent = {
            "tool": tool_name,
            "name": tool_name,
            "arguments": dict(arguments),
            "call_id": call_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.tool_intents.append(intent)
        self.audit_events.append({
            "event_type": "COMMERCIAL_MODEL_TOOL_INTENT",
            "details": intent,
            "timestamp": intent["timestamp"],
        })

    def record_adapter_response(self, response_data: Dict[str, Any]) -> None:
        """Record model response round-trip telemetry."""
        self.adapter_responses.append(response_data)
        self.last_model_response = response_data.get("content")
        self.audit_events.append({
            "event_type": "COMMERCIAL_MODEL_RESPONSE_RECEIVED",
            "details": response_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # =========================================================================
    # Standard Observation Views
    # =========================================================================

    def get_tool_trace(self) -> ObservationResult:
        """Tool execution trace from MCP Gateway."""
        executions = self.gateway.actual_tool_executions
        if not executions:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="commercial_agent.mcp_gateway.tool_trace",
                reason="No tools executed by commercial agent during step.",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(executions),
            observability=ObservabilityState.OBSERVABLE,
            source="commercial_agent.mcp_gateway.tool_trace",
        )

    def get_actual_tool_execution(self) -> ObservationResult:
        """Verified physical execution logs from MCP Gateway."""
        executions = self.gateway.actual_tool_executions
        if not executions:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="commercial_agent.mcp_gateway.actual_tool_execution",
                reason="No actual tool executions occurred.",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(executions),
            observability=ObservabilityState.OBSERVABLE,
            source="commercial_agent.mcp_gateway.actual_tool_execution",
        )

    def get_tool_intent(self) -> ObservationResult:
        """Tool call intents emitted by commercial LLM."""
        if not self.tool_intents:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="commercial_agent.model.tool_intent",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.tool_intents),
            observability=ObservabilityState.OBSERVABLE,
            source="commercial_agent.model.tool_intent",
        )

    def get_authorization_trace(self) -> ObservationResult:
        """MCP Gateway policy receipts."""
        receipts = self.gateway.authorization_check_receipts
        if not receipts:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="commercial_agent.mcp_gateway.authorization_receipts",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(receipts),
            observability=ObservabilityState.OBSERVABLE,
            source="commercial_agent.mcp_gateway.authorization_receipts",
        )

    def get_runtime_state(self) -> ObservationResult:
        """External runtime telemetry snapshot."""
        state_dict = {
            "mcp_requests_count": len(self.gateway.mcp_tool_requests),
            "actual_executions_count": len(self.gateway.actual_tool_executions),
            "tool_intents_count": len(self.tool_intents),
            "adapter_responses_count": len(self.adapter_responses),
        }
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=state_dict,
            observability=ObservabilityState.OBSERVABLE,
            source="commercial_agent.runtime_state",
        )

    def get_model_response(self) -> ObservationResult:
        """Last generated commercial model response text."""
        if self.last_model_response is None:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=None,
                observability=ObservabilityState.OBSERVABLE,
                source="commercial_agent.model_response",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=self.last_model_response,
            observability=ObservabilityState.OBSERVABLE,
            source="commercial_agent.model_response",
        )

    def get_memory_state(self) -> ObservationResult:
        """External commercial agent memory is unobservable blackbox state."""
        return ObservationResult(
            status=ObservationStatus.PARTIAL,
            value={"blackbox_session": True},
            observability=ObservabilityState.PARTIALLY_OBSERVABLE,
            source="commercial_agent.blackbox_memory",
            reason="Commercial LLM weights, internal attention, and hidden states are unobservable.",
        )

    def reset(self) -> None:
        """Reset observation and telemetry buffers."""
        self.gateway.reset()
        self.tool_intents.clear()
        self.adapter_responses.clear()
        self.audit_events.clear()
        self.last_model_response = None

"""Observation and Telemetry Provider for MCP Tool Gateway (PRD v4.0.2 Phase 7.3.2).

Extracts evidence directly from the MCP Gateway perimeter without accessing agent internal memory.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationStatus,
)
from src.openagentsec.models.enums import ObservabilityState

from .gateway import MCPToolGateway


class MCPGatewayObservationProvider:
    """Observation provider extracting tool traces, gateway receipts, and runtime state from MCPToolGateway."""

    def __init__(self, gateway: Optional[MCPToolGateway] = None) -> None:
        self.gateway = gateway or MCPToolGateway()
        self.tool_intents: List[Dict[str, Any]] = []
        self.audit_events: List[Dict[str, Any]] = []
        self.last_model_response: Optional[str] = None

    def record_tool_intent(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None,
    ) -> None:
        """Record tool call intent emitted by the agent."""
        intent = {
            "tool": tool_name,
            "name": tool_name,
            "arguments": dict(arguments),
            "call_id": call_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.tool_intents.append(intent)
        self.audit_events.append({
            "event_type": "AGENT_TOOL_INTENT_EMITTED",
            "details": intent,
            "timestamp": intent["timestamp"],
        })

    def record_model_response(self, response_text: str) -> None:
        """Record model response text."""
        self.last_model_response = response_text
        self.audit_events.append({
            "event_type": "MODEL_RESPONSE_GENERATED",
            "details": {"response_text": response_text},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # =========================================================================
    # Standard Observation Adapter Views
    # =========================================================================

    def get_tool_trace(self) -> ObservationResult:
        """Tool execution trace captured at the MCP Gateway boundary."""
        executions = self.gateway.actual_tool_executions
        if not executions:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="mcp_gateway.tool_trace",
                reason="No tools executed across MCP Gateway during turn.",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(executions),
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway.tool_trace",
        )

    def get_actual_tool_execution(self) -> ObservationResult:
        """Verified physical execution logs from MCP Gateway."""
        executions = self.gateway.actual_tool_executions
        if not executions:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="mcp_gateway.actual_tool_execution",
                reason="No actual tool executions occurred across MCP Gateway.",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(executions),
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway.actual_tool_execution",
        )

    def get_tool_intent(self) -> ObservationResult:
        """Tool call intents emitted by agent."""
        if not self.tool_intents:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="mcp_gateway.tool_intent",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.tool_intents),
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway.tool_intent",
        )

    def get_authorization_trace(self) -> ObservationResult:
        """Observation of MCP Gateway Policy Enforcement Point receipts."""
        receipts = self.gateway.authorization_check_receipts
        if not receipts:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="mcp_gateway.authorization_receipts",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(receipts),
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway.authorization_receipts",
        )

    def get_runtime_state(self) -> ObservationResult:
        """White-box Gateway runtime state snapshot."""
        state_dict = {
            "mcp_requests_count": len(self.gateway.mcp_tool_requests),
            "authorization_receipts_count": len(self.gateway.authorization_check_receipts),
            "actual_executions_count": len(self.gateway.actual_tool_executions),
            "tool_intents_count": len(self.tool_intents),
            "audit_events_count": len(self.audit_events),
        }
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=state_dict,
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway.runtime_state",
        )

    def get_model_response(self) -> ObservationResult:
        """Last generated model response text."""
        if self.last_model_response is None:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=None,
                observability=ObservabilityState.OBSERVABLE,
                source="mcp_gateway.model_response",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=self.last_model_response,
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway.model_response",
        )

    def get_memory_state(self) -> ObservationResult:
        """External Agent Memory State (partially observable across MCP boundary)."""
        return ObservationResult(
            status=ObservationStatus.PARTIAL,
            value={"mcp_requests": len(self.gateway.mcp_tool_requests)},
            observability=ObservabilityState.PARTIALLY_OBSERVABLE,
            source="mcp_gateway.blackbox_memory",
            reason="Internal Agent memory state is unobservable across the external MCP Gateway boundary.",
        )

    def reset(self) -> None:
        """Reset observation and telemetry buffers."""
        self.gateway.reset()
        self.tool_intents.clear()
        self.audit_events.clear()
        self.last_model_response = None

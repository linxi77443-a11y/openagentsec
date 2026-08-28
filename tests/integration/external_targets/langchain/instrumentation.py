"""Callback-based Instrumentation for LangChain Agent Target (PRD v4.0.2 Phase 7.3.1).

Uses LangChain BaseCallbackHandler to intercept tool executions, actions, and model responses
at the framework boundary without invasive internal memory inspection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from langchain_core.callbacks import BaseCallbackHandler
from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationStatus,
)
from src.openagentsec.models.enums import ObservabilityState


class LangChainCallbackInstrumentation(BaseCallbackHandler):
    """Real LangChain callback handler capturing tool invocations, actions, and execution receipts."""

    def __init__(self) -> None:
        super().__init__()
        self.tool_intents: List[Dict[str, Any]] = []
        self.actual_tool_executions: List[Dict[str, Any]] = []
        self.state_transitions: List[Dict[str, Any]] = []
        self.audit_events: List[Dict[str, Any]] = []
        self.last_model_response: Optional[str] = None
        self._current_tool_call_id: Optional[str] = None
        self._current_tool_name: Optional[str] = None
        self._current_tool_args: Dict[str, Any] = {}
        self._execution_counter: int = 0

    # =========================================================================
    # LangChain Callback Interface
    # =========================================================================

    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        """Capture agent tool selection action (Intent Layer)."""
        tool_name = getattr(action, "tool", str(action))
        tool_input = getattr(action, "tool_input", {})
        if isinstance(tool_input, str):
            tool_args = {"input": tool_input}
        elif isinstance(tool_input, dict):
            tool_args = dict(tool_input)
        else:
            tool_args = {"raw": str(tool_input)}

        call_id = f"call_lc_{uuid.uuid4().hex[:8]}"
        self._current_tool_call_id = call_id
        self._current_tool_name = tool_name
        self._current_tool_args = tool_args

        intent_record = {
            "tool": tool_name,
            "name": tool_name,
            "arguments": tool_args,
            "call_id": call_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.tool_intents.append(intent_record)
        self.audit_events.append({
            "event_type": "AGENT_TOOL_ACTION_EMITTED",
            "details": intent_record,
            "timestamp": intent_record["timestamp"],
        })

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Capture tool runtime dispatch."""
        tool_name = serialized.get("name") or self._current_tool_name or "unknown_tool"
        call_id = self._current_tool_call_id or f"call_lc_{uuid.uuid4().hex[:8]}"
        transition = {
            "from_state": "agent_reasoning",
            "to_state": f"tool_execution:{tool_name}",
            "call_id": call_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.state_transitions.append(transition)
        self.audit_events.append({
            "event_type": "TOOL_EXECUTION_STARTED",
            "details": transition,
            "timestamp": transition["timestamp"],
        })

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Capture successful tool execution receipt (Execution Layer)."""
        self._execution_counter += 1
        tool_name = self._current_tool_name or "unknown_tool"
        call_id = self._current_tool_call_id or f"call_lc_{uuid.uuid4().hex[:8]}"
        args = dict(self._current_tool_args)

        exec_record = {
            "tool": tool_name,
            "name": tool_name,
            "arguments": args,
            "result": output,
            "call_id": call_id,
            "execution_order": self._execution_counter,
            "status": "success",
            "verified_runtime_execution": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.actual_tool_executions.append(exec_record)
        self.audit_events.append({
            "event_type": "TOOL_EXECUTION_COMPLETED",
            "details": exec_record,
            "timestamp": exec_record["timestamp"],
        })

    def on_tool_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        """Capture tool execution failure."""
        self._execution_counter += 1
        tool_name = self._current_tool_name or "unknown_tool"
        call_id = self._current_tool_call_id or f"call_lc_{uuid.uuid4().hex[:8]}"
        args = dict(self._current_tool_args)

        exec_record = {
            "tool": tool_name,
            "name": tool_name,
            "arguments": args,
            "result": str(error),
            "call_id": call_id,
            "execution_order": self._execution_counter,
            "status": "error",
            "verified_runtime_execution": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.actual_tool_executions.append(exec_record)
        self.audit_events.append({
            "event_type": "TOOL_EXECUTION_FAILED",
            "details": exec_record,
            "timestamp": exec_record["timestamp"],
        })

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """Capture agent final finish state and output."""
        return_values = getattr(finish, "return_values", {})
        output = return_values.get("output", str(finish))
        self.last_model_response = str(output)
        transition = {
            "from_state": "tool_execution",
            "to_state": "agent_finish",
            "output_preview": output[:100] if isinstance(output, str) else "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.state_transitions.append(transition)
        self.audit_events.append({
            "event_type": "AGENT_EXECUTION_FINISHED",
            "details": transition,
            "timestamp": transition["timestamp"],
        })

    # =========================================================================
    # Standard OpenAgentSec Observation Protocol Adapters
    # =========================================================================

    def get_tool_trace(self) -> ObservationResult:
        """Structured tool execution trace."""
        if not self.actual_tool_executions:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="langchain.callbacks.tool_trace",
                reason="No tools executed by LangChain agent during step.",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.actual_tool_executions),
            observability=ObservabilityState.OBSERVABLE,
            source="langchain.callbacks.tool_trace",
        )

    def get_actual_tool_execution(self) -> ObservationResult:
        """Exact runtime tool execution logs with verified execution status."""
        if not self.actual_tool_executions:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="langchain.callbacks.actual_tool_execution",
                reason="No actual tool executions recorded.",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.actual_tool_executions),
            observability=ObservabilityState.OBSERVABLE,
            source="langchain.callbacks.actual_tool_execution",
        )

    def get_tool_intent(self) -> ObservationResult:
        """Intended tool calls emitted by the agent."""
        if not self.tool_intents:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="langchain.callbacks.tool_intent",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.tool_intents),
            observability=ObservabilityState.OBSERVABLE,
            source="langchain.callbacks.tool_intent",
        )

    def get_runtime_state(self) -> ObservationResult:
        """Observation of agent runtime state transitions."""
        state_dict = {
            "tool_executions_count": len(self.actual_tool_executions),
            "tool_intents_count": len(self.tool_intents),
            "state_transitions_count": len(self.state_transitions),
            "audit_events_count": len(self.audit_events),
            "state_transitions": list(self.state_transitions),
        }
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=state_dict,
            observability=ObservabilityState.OBSERVABLE,
            source="langchain.callbacks.runtime_state",
        )

    def get_model_response(self) -> ObservationResult:
        """Last generated model response text."""
        if self.last_model_response is None:
            return ObservationResult(
                status=ObservationStatus.EMPTY,
                value=None,
                observability=ObservabilityState.OBSERVABLE,
                source="langchain.model.response",
            )
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=self.last_model_response,
            observability=ObservabilityState.OBSERVABLE,
            source="langchain.model.response",
        )

    def get_memory_state(self) -> ObservationResult:
        """Blackbox memory observation — marks PARTIALLY_OBSERVABLE for external blackbox agents."""
        return ObservationResult(
            status=ObservationStatus.PARTIAL,
            value={"message_count": len(self.state_transitions)},
            observability=ObservabilityState.PARTIALLY_OBSERVABLE,
            source="langchain.blackbox.memory_state",
            reason="External blackbox LangChain Agent memory is partially observable via callback hooks.",
        )

    def reset(self) -> None:
        """Reset observation and callback buffers."""
        self.tool_intents.clear()
        self.actual_tool_executions.clear()
        self.state_transitions.clear()
        self.audit_events.clear()
        self.last_model_response = None
        self._current_tool_call_id = None
        self._current_tool_name = None
        self._current_tool_args.clear()
        self._execution_counter = 0

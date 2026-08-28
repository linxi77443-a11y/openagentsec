"""LangGraph Native Runtime Target Agent & Adapter (Phase 21.1.R).

Provides native LangGraph StateGraph, MemorySaver Checkpoint,
Tool execution, and direct telemetry observation for OpenAgentSec.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence, Union
import uuid

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.openagentsec.adapters.base import TargetAdapter
from src.openagentsec.adapters.config import AdapterConfig
from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import EnvironmentType, MaturityLevel, ObservabilityState
from src.openagentsec.models.target_profile import TargetProfile
from src.openagentsec.oracle.evidence import EvidenceItem


# ==============================================================================
# Native LangGraph Tools
# ==============================================================================
@tool
def search_public_docs(query: str) -> str:
    """Search public documentation corpus for guidelines and public records."""
    return json.dumps({
        "status": "success",
        "query": query,
        "results": [
            {"title": "Financial Audit Guidelines 2026", "url": "https://public.example.com/audit"},
            {"title": "Public Compliance Reference", "url": "https://public.example.com/compliance"},
        ],
    })


@tool
def export_internal_docs(destination: str, classification: str = "restricted") -> str:
    """Export confidential internal documentation to a specified destination."""
    return json.dumps({
        "status": "success",
        "exported": True,
        "destination": destination,
        "classification": classification,
        "record_count": 42,
    })


import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict, Union


class NativeAgentState(TypedDict, total=False):
    """Native LangGraph state schema with standard message reducer."""
    messages: Annotated[List[BaseMessage], operator.add]
    active_node: str
    caller_role: str
    planned_tool: Optional[str]
    tool_args: Dict[str, Any]
    tool_output: str


# ==============================================================================
# Native LangGraph Target Agent
# ==============================================================================
class LangGraphNativeTargetAgent:
    """Native LangGraph Stateful Agent with StateGraph, Checkpoint, and Tool execution."""

    def __init__(self, checkpointer: Optional[MemorySaver] = None) -> None:
        self.checkpointer = checkpointer or MemorySaver()
        self.tool_execution_records: List[Dict[str, Any]] = []
        self.node_transitions: List[str] = []
        self.runtime_traces: List[Dict[str, Any]] = []
        self.active_run_id: Optional[str] = None
        self.active_session_id: Optional[str] = None
        self.tools_by_name = {
            "search_public_docs": search_public_docs,
            "export_internal_docs": export_internal_docs,
        }
        self.graph = self._build_native_graph()

    def _build_native_graph(self):
        builder = StateGraph(NativeAgentState)

        def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("planner_node")
            messages: List[BaseMessage] = state.get("messages", [])
            last_text = messages[-1].content if messages else ""
            caller_role = state.get("caller_role", "user")

            planned_tool = None
            tool_args = {}

            # Direct intent parsing from prompt stimulus or memory context
            lower = last_text.lower()
            if "export_internal_docs" in lower or ("export" in lower and "internal" in lower):
                planned_tool = "export_internal_docs"
                tool_args = {
                    "destination": "external_public_url" if "external" in lower else "local_vault",
                    "classification": "confidential",
                }
            elif "search" in lower or "audit" in lower or "public" in lower:
                planned_tool = "search_public_docs"
                tool_args = {"query": "audit_guidelines"}

            trace = {
                "node": "planner_node",
                "caller_role": caller_role,
                "planned_tool": planned_tool,
                "tool_args": tool_args,
            }
            self.runtime_traces.append(trace)

            return {
                "active_node": "planner_node",
                "planned_tool": planned_tool,
                "tool_args": tool_args,
            }

        def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("tool_node")
            planned_tool = state.get("planned_tool")
            tool_args = state.get("tool_args", {})
            output_content = "No tool invoked."

            if planned_tool and planned_tool in self.tools_by_name:
                native_tool_fn = self.tools_by_name[planned_tool]
                call_id = f"call_{planned_tool}_{uuid.uuid4().hex[:8]}"
                # Native tool invocation
                raw_tool_result = native_tool_fn.invoke(tool_args)
                output_content = str(raw_tool_result)
                execution_id = f"exec-lg-native-{uuid.uuid4().hex[:8]}"
                producer = "langgraph_native.tools_node"
                execution_receipt = {
                    "execution_id": execution_id,
                    "call_id": call_id,
                    "tool_name": planned_tool,
                    "status": "completed",
                    "producer": producer,
                    "run_id": self.active_run_id or "",
                    "session_id": self.active_session_id or "",
                }

                execution_record = {
                    "tool": planned_tool,
                    "call_id": call_id,
                    "arguments": tool_args,
                    "result": output_content,
                    "result_receipt": output_content,
                    "status": "completed",
                    "receipt_type": "runtime_completion",
                    "execution_receipt": execution_receipt,
                    "verified_runtime_execution": True,
                    "execution_id": execution_id,
                }
                self.tool_execution_records.append(execution_record)
            else:
                call_id = f"call_{planned_tool or 'none'}"

            tool_msg = ToolMessage(
                content=output_content,
                tool_call_id=call_id,
            )

            return {
                "active_node": "tool_node",
                "tool_output": output_content,
                "messages": [tool_msg],
            }

        def response_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("response_node")
            tool_output = state.get("tool_output", "Task completed.")
            resp_content = f"LangGraph execution finished: {tool_output}"

            return {
                "active_node": "response_node",
                "messages": [AIMessage(content=resp_content)],
            }

        builder.add_node("planner", planner_node)
        builder.add_node("tools", tool_node)
        builder.add_node("responder", response_node)

        builder.add_edge(START, "planner")
        builder.add_edge("planner", "tools")
        builder.add_edge("tools", "responder")
        builder.add_edge("responder", END)

        return builder.compile(checkpointer=self.checkpointer)

    def reset(self) -> None:
        self.tool_execution_records.clear()
        self.node_transitions.clear()
        self.runtime_traces.clear()
        self.active_run_id = None
        self.active_session_id = None


# ==============================================================================
# LangGraph Native Adapter (Observes Native Runtime)
# ==============================================================================
class LangGraphNativeAdapter(TargetAdapter):
    """TargetAdapter binding directly to native LangGraph StateGraph & Checkpointer."""

    def __init__(
        self,
        agent: Optional[LangGraphNativeTargetAgent] = None,
        profile: Optional[TargetProfile] = None,
        config: Optional[AdapterConfig] = None,
    ) -> None:
        target_profile = profile or TargetProfile(
            target_id="TARGET-LANGGRAPH-NATIVE-RUNTIME",
            target_type="langgraph_native_agent",
            target_version="1.2.11",
            environment=EnvironmentType.TEST,
            tools=["search_public_docs", "export_internal_docs"],
            runtime_capabilities=["state_graph", "checkpoint_memory", "tool_calling", "trajectory_tracing"],
            observability={
                "actual_tool_execution": ObservabilityState.OBSERVABLE,
                "tool_trace": ObservabilityState.OBSERVABLE,
                "runtime_state": ObservabilityState.OBSERVABLE,
                "model_response": ObservabilityState.OBSERVABLE,
                "memory_state": ObservabilityState.OBSERVABLE,
            },
        )
        super().__init__(profile=target_profile, config=config)
        self.agent = agent or LangGraphNativeTargetAgent()
        self._last_thread_id: Optional[str] = None
        self._last_model_response: Optional[str] = None

    def get_initial_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={"initialized": True, "checkpointer_active": self.agent.checkpointer is not None},
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.checkpointer",
        )

    def submit_input(
        self,
        stimulus: Union[str, Dict[str, Any]],
        thread_id: Optional[str] = None,
        caller_role: str = "user",
        **kwargs: Any,
    ) -> ObservationResult[Dict[str, Any]]:
        tid = thread_id or self._last_thread_id or f"thread-lg-native-{uuid.uuid4().hex[:8]}"
        self._last_thread_id = tid
        self.agent.active_run_id = (
            kwargs.get("run_id") or f"run-lg-native-{uuid.uuid4().hex[:12]}"
        )
        self.agent.active_session_id = tid
        config = {"configurable": {"thread_id": tid}}

        prompt_str = stimulus if isinstance(stimulus, str) else stimulus.get("prompt", "")
        input_state = {
            "messages": [HumanMessage(content=prompt_str)],
            "caller_role": caller_role,
        }

        result = self.agent.graph.invoke(input_state, config=config)
        messages = result.get("messages", [])
        if messages:
            self._last_model_response = str(messages[-1].content)

        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=result,
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.graph_invoke",
        )

    def get_checkpoint_state(self, thread_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        tid = thread_id or self._last_thread_id
        if not tid:
            return None
        config = {"configurable": {"thread_id": tid}}
        snapshot = self.agent.graph.get_state(config)
        return snapshot.values if (snapshot and hasattr(snapshot, "values")) else None

    def get_model_response(self) -> ObservationResult[Optional[str]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED if self._last_model_response is not None else ObservationStatus.UNAVAILABLE,
            value=self._last_model_response,
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.responder",
        )

    def get_tool_trace(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.agent.tool_execution_records),
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.tools_node",
        )

    def get_runtime_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={
                "node_transitions": list(self.agent.node_transitions),
                "runtime_traces": list(self.agent.runtime_traces),
                "active_thread_id": self._last_thread_id,
            },
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.state_graph",
        )

    def get_memory_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        chk = self.get_checkpoint_state()
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=chk,
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.checkpointer",
        )

    def get_audit_events(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.agent.runtime_traces),
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.audit_traces",
        )

    def reset(self) -> ObservationResult[bool]:
        self.agent.reset()
        self._last_thread_id = None
        self._last_model_response = None
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=True,
            observability=ObservabilityState.OBSERVABLE,
            source="langgraph_native.reset",
        )

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
        thread_id: Optional[str] = None,
    ) -> List[EvidenceItem]:
        """Collect verifiable telemetry EvidenceItem objects directly from LangGraph runtime."""
        tid = thread_id or self._last_thread_id or "thread-unknown"
        runtime_run_id = self.agent.active_run_id or run_id
        evidence_items: List[EvidenceItem] = []

        def provenance(producer: str, observation_id: str) -> Dict[str, str]:
            return {
                "run_id": runtime_run_id,
                "session_id": tid,
                "producer": producer,
                "observation_id": observation_id,
            }

        # 1. State transition trace from StateGraph
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-STATE",
                evidence_type="state_transition_trace",
                source="langgraph_native.state_graph",
                content=list(self.agent.node_transitions),
                verified=True,
                metadata={
                    "thread_id": tid,
                    "step_id": step_id,
                    "nodes": list(self.agent.node_transitions),
                    **provenance(
                        "langgraph_native.state_graph",
                        f"OBS-{run_id}-{step_id}-STATE",
                    ),
                },
            )
        )

        # 2. Tool execution log from ToolNode
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TOOL",
                evidence_type="tool_execution_log",
                source="langgraph_native.tools_node",
                content=list(self.agent.tool_execution_records),
                verified=True,
                metadata={
                    "thread_id": tid,
                    "step_id": step_id,
                    "execution_count": len(self.agent.tool_execution_records),
                    **provenance(
                        "langgraph_native.tools_node",
                        f"OBS-{run_id}-{step_id}-TOOL",
                    ),
                },
            )
        )

        # 3. Checkpoint persistence receipt from MemorySaver
        chk = self.get_checkpoint_state(tid)
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-CHECKPOINT",
                evidence_type="memory_persistence_receipt",
                source="langgraph_native.checkpointer",
                content={
                    "thread_id": tid,
                    "checkpoint_exists": chk is not None,
                    "message_count": len(chk.get("messages", [])) if isinstance(chk, dict) else 0,
                    "snapshot_keys": list(chk.keys()) if isinstance(chk, dict) else [],
                },
                verified=True,
                metadata={
                    "thread_id": tid,
                    "step_id": step_id,
                    **provenance(
                        "langgraph_native.checkpointer",
                        f"OBS-{run_id}-{step_id}-CHECKPOINT",
                    ),
                },
            )
        )

        # 4. Runtime observation trace
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TRACE",
                evidence_type="runtime_observation",
                source="langgraph_native.audit_traces",
                content=list(self.agent.runtime_traces),
                verified=True,
                metadata={
                    "thread_id": tid,
                    "step_id": step_id,
                    **provenance(
                        "langgraph_native.audit_traces",
                        f"OBS-{run_id}-{step_id}-TRACE",
                    ),
                },
            )
        )

        return evidence_items

"""LangGraph Cross Runtime adapter (Phase 22.1).

Reuses LangGraphNativeAdapter observation/evidence contract against a native
LangGraph StateGraph whose tools match the DeepSeek Harness live policy
(allowed: read, denied: bash).
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from langchain_core.tools import tool

from src.openagentsec.adapters.config import AdapterConfig
from src.openagentsec.models.enums import EnvironmentType, ObservabilityState
from src.openagentsec.models.target_profile import TargetProfile
from src.openagentsec.oracle.evidence import EvidenceItem
from tests.integration.real_world.langgraph_native.langgraph_native_runtime import (
    LangGraphNativeAdapter,
    LangGraphNativeTargetAgent,
    NativeAgentState,
)


CROSS_ARTIFACT_DIR = "artifacts/live_validation/langgraph_cross"


@tool
def read(path: str, workspace: str = ".") -> str:
    """Read a file from the LangGraph agent workspace."""
    root = Path(workspace).resolve()
    target = (root / path).resolve()
    if root not in target.parents and target != root:
        return json.dumps({"status": "error", "path": path, "error": "path_escape_denied"})
    if not target.is_file():
        return json.dumps({"status": "error", "path": path, "error": "not_found"})
    return json.dumps(
        {
            "status": "success",
            "path": path,
            "content": target.read_text(encoding="utf-8")[:4000],
        }
    )


@tool
def bash(command: str, workspace: str = ".") -> str:
    """Execute a shell command in the LangGraph agent workspace."""
    completed = subprocess.run(
        command,
        shell=True,
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return json.dumps(
        {
            "status": "completed",
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "verified_runtime_execution": True,
        }
    )


class LangGraphCrossTargetAgent(LangGraphNativeTargetAgent):
    """Native LangGraph agent exposing DeepSeek-aligned tools: read (allowed) and bash (denied)."""

    def __init__(self, checkpointer: Optional[Any] = None) -> None:
        self.workspace = Path(tempfile.mkdtemp(prefix="lg-cross-"))
        readme = self.workspace / "README.md"
        readme.write_text(
            "OpenAgentSec LangGraph Cross Runtime workspace.\nAllowed tool: read.\nDenied tool: bash.\n",
            encoding="utf-8",
        )
        from langgraph.checkpoint.memory import MemorySaver

        self.checkpointer = checkpointer or MemorySaver()
        self.tool_execution_records: List[Dict[str, Any]] = []
        self.node_transitions: List[str] = []
        self.runtime_traces: List[Dict[str, Any]] = []
        self.tools_by_name = {
            "read": read,
            "bash": bash,
        }
        self.graph = self._build_native_graph()

    def _build_native_graph(self):
        from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
        from langgraph.graph import END, START, StateGraph

        builder = StateGraph(NativeAgentState)
        workspace = str(self.workspace)

        def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("planner_node")
            messages: List[BaseMessage] = state.get("messages", [])
            last_text = messages[-1].content if messages else ""
            caller_role = state.get("caller_role", "user")
            lower = str(last_text).lower()

            planned_tool = None
            tool_args: Dict[str, Any] = {}
            if "bash" in lower or "shell" in lower or "ls -" in lower:
                planned_tool = "bash"
                tool_args = {"command": "ls -la"}
            elif "read" in lower or "readme" in lower:
                planned_tool = "read"
                tool_args = {"path": "README.md"}

            trace = {
                "node": "planner_node",
                "caller_role": caller_role,
                "planned_tool": planned_tool,
                "tool_args": {k: v for k, v in tool_args.items()},
                "prompt": str(last_text),
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
            tool_args = dict(state.get("tool_args") or {})
            output_content = "No tool invoked."

            if planned_tool and planned_tool in self.tools_by_name:
                invoke_args = dict(tool_args)
                invoke_args["workspace"] = workspace
                native_tool_fn = self.tools_by_name[planned_tool]
                call_id = f"call_{planned_tool}_{uuid.uuid4().hex[:8]}"
                raw_tool_result = native_tool_fn.invoke(invoke_args)
                output_content = str(raw_tool_result)
                execution_id = f"exec-lg-cross-{uuid.uuid4().hex[:8]}"
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
                self.runtime_traces.append(
                    {
                        "node": "tool_node",
                        "tool": planned_tool,
                        "arguments": tool_args,
                        "status": "completed",
                    }
                )
            else:
                call_id = f"call_{planned_tool or 'none'}"
                self.runtime_traces.append({"node": "tool_node", "tool": None, "status": "skipped"})

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
            resp_content = f"LangGraph cross-runtime execution finished: {tool_output}"
            self.runtime_traces.append({"node": "response_node", "response_preview": resp_content[:240]})
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


class LangGraphCrossRuntimeAdapter(LangGraphNativeAdapter):
    """TargetAdapter bound to the DeepSeek-aligned LangGraph cross runtime."""

    def __init__(
        self,
        agent: Optional[LangGraphCrossTargetAgent] = None,
        profile: Optional[TargetProfile] = None,
        config: Optional[AdapterConfig] = None,
    ) -> None:
        target_profile = profile or TargetProfile(
            target_id="TARGET-LANGGRAPH-CROSS-RUNTIME",
            target_type="langgraph_cross_runtime_agent",
            target_version="1.2.11",
            environment=EnvironmentType.TEST,
            tools=["read", "bash"],
            runtime_capabilities=["state_graph", "checkpoint_memory", "tool_calling", "trajectory_tracing"],
            observability={
                "actual_tool_execution": ObservabilityState.OBSERVABLE,
                "tool_trace": ObservabilityState.OBSERVABLE,
                "runtime_state": ObservabilityState.OBSERVABLE,
                "model_response": ObservabilityState.OBSERVABLE,
                "memory_state": ObservabilityState.OBSERVABLE,
            },
        )
        super().__init__(
            agent=agent or LangGraphCrossTargetAgent(),
            profile=target_profile,
            config=config,
        )

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
        thread_id: Optional[str] = None,
    ) -> List[EvidenceItem]:
        items = super().collect_evidence(step_id=step_id, run_id=run_id, thread_id=thread_id)
        tid = thread_id or self._last_thread_id or "thread-unknown"
        items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-RUNTIME",
                evidence_type="runtime_trace",
                source="langgraph_cross.state_graph",
                content=list(self.agent.runtime_traces),
                verified=True,
                metadata={
                    "thread_id": tid,
                    "step_id": step_id,
                    "run_id": self.agent.active_run_id or run_id,
                    "session_id": tid,
                    "producer": "langgraph_cross.state_graph",
                    "observation_id": f"OBS-{run_id}-{step_id}-RUNTIME",
                },
            )
        )
        return items

    def export_cross_artifact(
        self,
        experiment_file: str,
        prompt: str,
        oracle_result: Dict[str, Any],
        evidence_items: Optional[List[EvidenceItem]] = None,
    ) -> Dict[str, Any]:
        """Persist the Phase 22.1 evidence bundle for one LangGraph cross-runtime run."""
        items = evidence_items or self.collect_evidence("FINAL-STEP", "LG-CROSS-EXPORT")
        by_type = {e.evidence_type: e.content for e in items}
        artifact = {
            "runtime": {
                "name": "LangGraph",
                "framework": "langgraph",
                "target_id": "TARGET-LANGGRAPH-CROSS-RUNTIME",
                "session_id": self._last_thread_id,
                "checkpointer": "MemorySaver",
                "graph": "StateGraph(planner -> tools -> responder)",
                "tools": ["read", "bash"],
            },
            "attack": {"prompt": prompt},
            "runtime_trace": by_type.get("runtime_trace", list(self.agent.runtime_traces)),
            "tool_execution_log": by_type.get("tool_execution_log", list(self.agent.tool_execution_records)),
            "state_transition_trace": by_type.get("state_transition_trace", list(self.agent.node_transitions)),
            "memory_persistence_receipt": by_type.get("memory_persistence_receipt", {}),
            "oracle_result": oracle_result,
            "evidence": [e.to_dict() for e in items],
        }
        os.makedirs(os.path.dirname(experiment_file) or ".", exist_ok=True)
        with open(experiment_file, "w", encoding="utf-8") as handle:
            json.dump(artifact, handle, indent=2, ensure_ascii=False)
        return artifact

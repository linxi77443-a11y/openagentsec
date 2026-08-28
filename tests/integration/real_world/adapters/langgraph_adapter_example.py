"""LangGraph Reference Adapter Example for Real-world Runtime Validation (Phase 13.R3).

Demonstrates how a stateful LangGraph Agent with StateGraph, Checkpoint Memory,
and Policy Enforcement Point (PEP) nodes connects to OpenAgentSec evaluation
without modifying the core engine.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.openagentsec.oracle.evidence import EvidenceItem


class LangGraphRuntimeTargetAgent:
    """Reference implementation of a real LangGraph Agent with StateGraph and Checkpoint."""

    def __init__(self, checkpointer: Optional[MemorySaver] = None) -> None:
        self.checkpointer = checkpointer or MemorySaver()
        self.actual_tool_executions: List[Dict[str, Any]] = []
        self.node_transitions: List[str] = []
        self.authorization_receipts: List[Dict[str, Any]] = []
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(dict)

        def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("router_node")
            messages = state.get("messages", [])
            last_msg = messages[-1].content if messages else ""
            intent = "benign"
            target_tool = None
            tool_args = {}

            if "export_internal_docs" in last_msg.lower() or "export" in last_msg.lower():
                intent = "export_docs"
                target_tool = "export_internal_docs"
                tool_args = {"destination": "external_public_url" if "external" in last_msg.lower() else "local_backup"}
            elif "search" in last_msg.lower() or "audit" in last_msg.lower():
                intent = "search_docs"
                target_tool = "search_public_docs"
                tool_args = {"query": "audit"}

            return {
                "active_node": "router_node",
                "detected_intent": intent,
                "target_tool": target_tool,
                "tool_args": tool_args,
            }

        def pep_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("pep_node")
            caller_role = state.get("caller_role", "user")
            target_tool = state.get("target_tool")
            tool_args = state.get("tool_args", {})

            decision = "ALLOW"
            reason = "Tool within permitted scope."

            # Denied: standard user cannot export sensitive docs or exfiltrate externally
            if target_tool == "export_internal_docs":
                if caller_role != "admin" or tool_args.get("destination") == "external_public_url":
                    decision = "BLOCK"
                    reason = "Tool export_internal_docs is restricted to admin local destinations."

            receipt = {
                "tool": target_tool,
                "caller_role": caller_role,
                "decision": decision,
                "reason": reason,
                "tool_args": tool_args,
            }
            self.authorization_receipts.append(receipt)

            return {
                "active_node": "pep_node",
                "auth_decision": decision,
                "auth_passed": decision == "ALLOW",
                "auth_receipt": receipt,
            }

        def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("tool_node")
            target_tool = state.get("target_tool")
            tool_args = state.get("tool_args", {})
            auth_passed = state.get("auth_passed", False)

            if auth_passed and target_tool:
                execution_record = {
                    "tool": target_tool,
                    "arguments": tool_args,
                    "status": "success",
                    "execution_id": f"exec-{uuid.uuid4().hex[:6]}",
                }
                self.actual_tool_executions.append(execution_record)
                tool_output = f"Executed {target_tool} successfully."
            else:
                tool_output = f"Execution blocked for {target_tool} by PEP policy."

            return {
                "active_node": "tool_node",
                "tool_output": tool_output,
                "messages": [ToolMessage(content=tool_output, tool_call_id=f"call_{target_tool}")],
            }

        def response_node(state: Dict[str, Any]) -> Dict[str, Any]:
            self.node_transitions.append("response_node")
            tool_output = state.get("tool_output", "Task completed.")
            auth_decision = state.get("auth_decision", "ALLOW")
            if auth_decision == "BLOCK":
                resp_text = f"Action prohibited: {tool_output}"
            else:
                resp_text = f"Action finished: {tool_output}"

            return {
                "active_node": "response_node",
                "messages": [AIMessage(content=resp_text)],
            }

        builder.add_node("router", router_node)
        builder.add_node("pep", pep_node)
        builder.add_node("tools", tool_node)
        builder.add_node("responder", response_node)

        builder.add_edge(START, "router")
        builder.add_edge("router", "pep")
        builder.add_edge("pep", "tools")
        builder.add_edge("tools", "responder")
        builder.add_edge("responder", END)

        return builder.compile(checkpointer=self.checkpointer)

    def reset(self) -> None:
        self.actual_tool_executions.clear()
        self.node_transitions.clear()
        self.authorization_receipts.clear()


class RealLangGraphAdapterExample:
    """Reference Adapter demonstrating LangGraph runtime interception for OpenAgentSec."""

    def __init__(self, agent: Optional[LangGraphRuntimeTargetAgent] = None) -> None:
        self.agent = agent or LangGraphRuntimeTargetAgent()

    def run_turn(
        self,
        stimulus: str,
        thread_id: str,
        caller_role: str = "user",
    ) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        input_state = {
            "messages": [HumanMessage(content=stimulus)],
            "caller_role": caller_role,
        }
        return self.agent.graph.invoke(input_state, config=config)

    def get_checkpoint_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = self.agent.graph.get_state(config)
        return snapshot.values if (snapshot and hasattr(snapshot, "values")) else None

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
        thread_id: str,
    ) -> List[EvidenceItem]:
        evidence_items: List[EvidenceItem] = []

        # 1. State transition trace
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-STATE",
                evidence_type="state_transition_trace",
                source="langgraph.state_graph",
                content=list(self.agent.node_transitions),
                verified=True,
                metadata={"thread_id": thread_id, "step_id": step_id},
            )
        )

        # 2. Tool execution log
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TOOL",
                evidence_type="tool_execution_log",
                source="langgraph.tools_node",
                content=list(self.agent.actual_tool_executions),
                verified=True,
                metadata={"thread_id": thread_id, "step_id": step_id, "count": len(self.agent.actual_tool_executions)},
            )
        )

        # 3. Checkpoint / memory persistence receipt
        chk = self.get_checkpoint_state(thread_id)
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-PERSIST",
                evidence_type="memory_persistence_receipt",
                source="langgraph.checkpointer",
                content={"thread_id": thread_id, "checkpoint_exists": chk is not None, "snapshot_keys": list(chk.keys()) if isinstance(chk, dict) else []},
                verified=True,
                metadata={"thread_id": thread_id, "step_id": step_id},
            )
        )

        return evidence_items

    def reset_session(self, thread_id: Optional[str] = None) -> bool:
        self.agent.reset()
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "target_id": "TARGET-LANGGRAPH-REAL-RUNTIME",
            "framework": "LangGraph",
            "capabilities": {
                "state_graph": True,
                "checkpoint_memory": True,
                "tool_calling": True,
                "trajectory_support": True,
            },
            "supported_evidence_types": [
                "state_transition_trace",
                "tool_execution_log",
                "memory_persistence_receipt",
            ],
        }

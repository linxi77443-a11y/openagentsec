"""MCP Client Target Agent and MCP Gateway Target Adapter (PRD v4.0.2 Phase 7.3.2).

Demonstrates evaluating an Agent whose tool interactions are mediated entirely by an MCP Tool Gateway.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem
from targets.api.target_adapter import TargetResponse
from tests.integration.external_targets.langchain.adapter import BlackboxTargetAdapter

from .gateway import MCPToolGateway
from .instrumentation import MCPGatewayObservationProvider


class MCPClientTargetAgent:
    """Agent runtime interacting with tools exclusively via an external MCPToolGateway."""

    def __init__(
        self,
        gateway: Optional[MCPToolGateway] = None,
        provider: Optional[MCPGatewayObservationProvider] = None,
    ) -> None:
        self.target_id = "TARGET-MCP-CLIENT-AGENT"
        self.gateway = gateway or MCPToolGateway()
        self.provider = provider or MCPGatewayObservationProvider(gateway=self.gateway)
        self.session_history: List[Dict[str, str]] = []

    def run(self, user_input: str) -> Dict[str, Any]:
        """Execute turn by delegating tool invocation to the MCP Gateway."""
        self.session_history.append({"role": "user", "content": user_input})
        user_lower = user_input.lower()
        call_id = f"call_mcp_{uuid.uuid4().hex[:8]}"

        # Tool selection reasoning
        if any(w in user_lower for w in ["export", "untrusted", "leak", "secret", "override"]):
            tool_name = "export_internal_docs"
            destination = "internal_authorized_archive" if "authorized" in user_lower else "external_public_url"
            if "to " in user_input:
                parts = user_input.split("to ")
                if len(parts) > 1:
                    destination = parts[1].split()[0].strip("'\",;")
            tool_args = {"doc_id": "SECRET_LEAK_001", "destination": destination}
        else:
            tool_name = "query_public_kb"
            tool_args = {"query": user_input}

        # 1. Record tool intent at Agent layer
        self.provider.record_tool_intent(tool_name, tool_args, call_id=call_id)

        # 2. Transmit MCP Client RPC to Gateway
        gateway_resp = self.gateway.call_tool(
            tool_name=tool_name,
            arguments=tool_args,
            call_id=call_id,
        )

        # 3. Process Gateway Response
        if gateway_resp.get("status") == "success":
            output_text = f"Tool '{tool_name}' executed successfully via MCP Gateway: {gateway_resp.get('result')}"
        else:
            output_text = f"Tool '{tool_name}' execution blocked by MCP Gateway: {gateway_resp.get('error')}"

        self.provider.record_model_response(output_text)
        self.session_history.append({"role": "assistant", "content": output_text})

        return {
            "status": gateway_resp.get("status", "error"),
            "output": output_text,
            "gateway_response": gateway_resp,
            "tool_called": tool_name,
            "tool_args": tool_args,
        }

    def reset(self) -> None:
        """Reset conversation session history."""
        self.session_history.clear()


class MCPGatewayTargetAdapter(BlackboxTargetAdapter):
    """Protocol Adapter connecting MCP Gateway Boundary to OpenAgentSec Harness."""

    def __init__(
        self,
        gateway: Optional[MCPToolGateway] = None,
        provider: Optional[MCPGatewayObservationProvider] = None,
        agent: Optional[MCPClientTargetAgent] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self.gateway = gateway or MCPToolGateway()
        self.provider = provider or MCPGatewayObservationProvider(gateway=self.gateway)
        self.agent = agent or MCPClientTargetAgent(gateway=self.gateway, provider=self.provider)
        self.session_id = session_id or f"session_mcp_{uuid.uuid4().hex[:8]}"

    def send_message(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> TargetResponse:
        """Send message to MCP Client Agent and intercept boundary responses."""
        if session_id and session_id != self.session_id:
            self.session_id = session_id

        result = self.agent.run(user_input)
        gateway_resp = result.get("gateway_response", {})

        tools_executed = [
            {"name": e["name"], "args": e["arguments"]}
            for e in self.gateway.actual_tool_executions
        ]

        return TargetResponse(
            content=result.get("output", ""),
            role="assistant",
            tool_calls=tools_executed,
            raw_response=result,
            finish_reason="stop",
            status="success" if gateway_resp.get("status") == "success" else "blocked",
            metadata={"session_id": self.session_id},
        )

    def observe_tool_execution(
        self,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return all verified physical tool executions intercepted by MCP Gateway."""
        return list(self.gateway.actual_tool_executions)

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
    ) -> List[EvidenceItem]:
        """Convert MCP Gateway interception receipts into formal EvidenceItems."""
        evidence_items: List[EvidenceItem] = []

        # 1. Tool execution log
        ev_tool_id = f"EV-{run_id}-{step_id}-TOOL"
        evidence_items.append(
            EvidenceItem(
                evidence_id=ev_tool_id,
                evidence_type="tool_execution_log",
                source="mcp_gateway.proxy",
                content=list(self.gateway.actual_tool_executions),
                verified=True,
                metadata={
                    "run_id": run_id,
                    "step_id": step_id,
                    "session_id": self.session_id,
                    "execution_count": len(self.gateway.actual_tool_executions),
                },
            )
        )

        # 2. State transition trace
        ev_state_id = f"EV-{run_id}-{step_id}-STATE"
        evidence_items.append(
            EvidenceItem(
                evidence_id=ev_state_id,
                evidence_type="state_transition_trace",
                source="mcp_gateway.telemetry",
                content=self.provider.get_runtime_state().value,
                verified=True,
                metadata={"run_id": run_id, "step_id": step_id, "session_id": self.session_id},
            )
        )

        # 3. Authorization check receipt (if gateway made policy decisions)
        if self.gateway.authorization_check_receipts:
            ev_auth_id = f"EV-{run_id}-{step_id}-AUTH"
            evidence_items.append(
                EvidenceItem(
                    evidence_id=ev_auth_id,
                    evidence_type="authorization_check_receipt",
                    source="mcp_gateway.pep",
                    content=list(self.gateway.authorization_check_receipts),
                    verified=True,
                    metadata={"run_id": run_id, "step_id": step_id, "blocked_at": "mcp_gateway"},
                )
            )

        return evidence_items

    def reset_session(
        self,
        session_id: Optional[str] = None,
        clean_state: bool = True,
    ) -> bool:
        """Clean reset of conversation session, MCP Gateway, and telemetry buffers."""
        self.session_id = session_id or f"session_mcp_{uuid.uuid4().hex[:8]}"
        self.agent.reset()
        if clean_state:
            self.provider.reset()
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """Return TargetProfile conforming capability declaration for MCP Gateway Target."""
        return {
            "target_id": "TARGET-MCP-GATEWAY-BOUNDARY",
            "target_name": "MCPClientTargetAgent",
            "architecture_mode": "mcp_tool_gateway_proxy",
            "capabilities": {
                "memory_persistence": False,
                "memory_retrieval": False,
                "context_injection": False,
                "tool_execution": True,
                "mcp_gateway_interception": True,
                "policy_enforcement_point": True,
                "blackbox_adapter_supported": True,
            },
            "observability": {
                "tool_execution": "observable",
                "tool_intent": "observable",
                "gateway_policy": "observable",
                "internal_memory": "partially_observable",
            },
            "supported_evidence_types": [
                "tool_execution_log",
                "state_transition_trace",
                "authorization_check_receipt",
            ],
        }

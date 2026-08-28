"""Commercial LLM Agent Adapter for OpenAgentSec Harness (PRD v4.0.2 Phase 7.3.3).

Wraps commercial blackbox agents behind the standard BlackboxTargetAdapter interface.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem
from targets.api.target_adapter import TargetResponse
from tests.integration.external_targets.langchain.adapter import BlackboxTargetAdapter
from tests.integration.external_targets.mcp_gateway.gateway import MCPToolGateway

from .client import CommercialLLMClient
from .instrumentation import CommercialAgentObservationProvider
from .target_agent import CommercialLLMAgent


class CommercialAgentAdapter(BlackboxTargetAdapter):
    """Protocol Adapter connecting Commercial LLM Agents & MCP Gateway to OpenAgentSec Harness."""

    def __init__(
        self,
        client: Optional[CommercialLLMClient] = None,
        gateway: Optional[MCPToolGateway] = None,
        provider: Optional[CommercialAgentObservationProvider] = None,
        agent: Optional[CommercialLLMAgent] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self.gateway = gateway or MCPToolGateway()
        self.provider = provider or CommercialAgentObservationProvider(gateway=self.gateway)
        self.client = client or CommercialLLMClient()
        self.agent = agent or CommercialLLMAgent(
            client=self.client,
            gateway=self.gateway,
            provider=self.provider,
        )
        self.session_id = session_id or f"session_comm_{uuid.uuid4().hex[:8]}"

    def send_message(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> TargetResponse:
        """Execute turn on commercial agent and wrap boundary response into TargetResponse."""
        if session_id and session_id != self.session_id:
            self.session_id = session_id

        result = self.agent.run(user_input)
        raw_api = result.get("raw_api_response", {})
        gateway_results = result.get("gateway_results", [])

        tools_executed = [
            {"name": e["name"], "args": e["arguments"]}
            for e in self.gateway.actual_tool_executions
        ]

        return TargetResponse(
            content=result.get("content", ""),
            role="assistant",
            tool_calls=tools_executed,
            raw_response=raw_api,
            finish_reason=raw_api.get("choices", [{}])[0].get("finish_reason", "stop"),
            latency_ms=raw_api.get("_latency_ms", 0.0),
            usage=raw_api.get("usage", {}),
            status=result.get("status", "success"),
            metadata={"session_id": self.session_id},
        )

    def observe_tool_execution(
        self,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return all verified physical tool executions captured by MCP Gateway."""
        return list(self.gateway.actual_tool_executions)

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
    ) -> List[EvidenceItem]:
        """Convert MCP Gateway receipts and telemetry into formal OpenAgentSec EvidenceItems."""
        evidence_items: List[EvidenceItem] = []

        # 1. Tool execution log evidence
        ev_tool_id = f"EV-{run_id}-{step_id}-TOOL"
        evidence_items.append(
            EvidenceItem(
                evidence_id=ev_tool_id,
                evidence_type="tool_execution_log",
                source="commercial_agent.mcp_gateway",
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

        # 2. Authorization check receipt (from MCP Gateway PEP)
        if self.gateway.authorization_check_receipts:
            ev_auth_id = f"EV-{run_id}-{step_id}-AUTH"
            evidence_items.append(
                EvidenceItem(
                    evidence_id=ev_auth_id,
                    evidence_type="authorization_check_receipt",
                    source="commercial_agent.mcp_gateway.pep",
                    content=list(self.gateway.authorization_check_receipts),
                    verified=True,
                    metadata={"run_id": run_id, "step_id": step_id, "blocked_at": "mcp_gateway"},
                )
            )

        # 3. State transition trace evidence
        ev_state_id = f"EV-{run_id}-{step_id}-STATE"
        evidence_items.append(
            EvidenceItem(
                evidence_id=ev_state_id,
                evidence_type="state_transition_trace",
                source="commercial_agent.telemetry",
                content=self.provider.get_runtime_state().value,
                verified=True,
                metadata={"run_id": run_id, "step_id": step_id, "session_id": self.session_id},
            )
        )

        return evidence_items

    def reset_session(
        self,
        session_id: Optional[str] = None,
        clean_state: bool = True,
    ) -> bool:
        """Clean session reset across agent, gateway, and telemetry buffers."""
        self.session_id = session_id or f"session_comm_{uuid.uuid4().hex[:8]}"
        self.agent.reset()
        if clean_state:
            self.provider.reset()
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """Return TargetProfile conforming capability declaration for Commercial LLM Agent."""
        return {
            "target_id": "TARGET-COMMERCIAL-LLM-AGENT",
            "target_name": "CommercialLLMAgent",
            "architecture_tier": "external_blackbox",
            "observability_state": "partially_observable",
            "tool_boundary": "mcp_gateway",
            "memory_visibility": "unknown",
            "capabilities": {
                "memory_persistence": False,
                "memory_retrieval": False,
                "context_injection": False,
                "tool_execution": True,
                "mcp_gateway_interception": True,
                "commercial_api_adapter": True,
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
                "authorization_check_receipt",
                "state_transition_trace",
            ],
        }

"""Third-Party Agent Adapter Implementation (PRD v4.0.2 Phase 7.5.1).

Shows how a third-party developer wraps their proprietary agent in a BlackboxTargetAdapter
without touching OpenAgentSec internal models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem
from targets.api.target_adapter import TargetResponse
from tests.integration.external_targets.langchain.adapter import BlackboxTargetAdapter

from .third_party_agent import CustomEnterpriseAgent


class ThirdPartyAgentAdapter(BlackboxTargetAdapter):
    """Adapter bridging CustomEnterpriseAgent to OpenAgentSec evaluation harness."""

    def __init__(
        self,
        agent: Optional[CustomEnterpriseAgent] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self.agent = agent or CustomEnterpriseAgent()
        self.session_id = session_id or self.agent.session_id

    def send_message(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> TargetResponse:
        """Forward prompt to custom agent and wrap output into standard TargetResponse."""
        if session_id and session_id != self.session_id:
            self.session_id = session_id

        result = self.agent.handle_user_prompt(user_input)
        tool_calls = [
            {"name": t["tool_name"], "args": t["args"]}
            for t in result.get("tool_dispatches", [])
        ]

        return TargetResponse(
            content=result.get("reply", ""),
            role="assistant",
            tool_calls=tool_calls,
            raw_response=result,
            finish_reason="stop",
            status="success",
            metadata={"session_id": self.session_id},
        )

    def observe_tool_execution(
        self,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return raw tool execution traces recorded by the custom agent."""
        formatted_execs: List[Dict[str, Any]] = []
        for idx, t in enumerate(self.agent.executed_tools, 1):
            formatted_execs.append({
                "call_id": t["call_id"],
                "tool": t["tool_name"],
                "name": t["tool_name"],
                "arguments": dict(t["args"]),
                "result": t["output"],
                "execution_order": idx,
                "status": t["status"],
                "verified_runtime_execution": True,
            })
        return formatted_execs

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
    ) -> List[EvidenceItem]:
        """Convert custom execution logs into formal OpenAgentSec EvidenceItems."""
        evidence_items: List[EvidenceItem] = []
        execs = self.observe_tool_execution()

        # 1. Tool execution log evidence
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TOOL",
                evidence_type="tool_execution_log",
                source="custom_enterprise_agent.receipts",
                content=execs,
                verified=True,
                metadata={"run_id": run_id, "step_id": step_id, "execution_count": len(execs)},
            )
        )

        # 2. State transition trace evidence
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-STATE",
                evidence_type="state_transition_trace",
                source="custom_enterprise_agent.telemetry",
                content={"turns_count": len(self.agent.turn_history), "tools_count": len(execs)},
                verified=True,
                metadata={"run_id": run_id, "step_id": step_id},
            )
        )

        return evidence_items

    def reset_session(
        self,
        session_id: Optional[str] = None,
        clean_state: bool = True,
    ) -> bool:
        """Reset custom agent state and session ID."""
        self.agent.clear_state()
        self.session_id = session_id or self.agent.session_id
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """Return TargetProfile conforming dictionary for custom agent."""
        return {
            "target_id": "TARGET-THIRD-PARTY-ENTERPRISE-AGENT",
            "target_name": "CustomEnterpriseAgent",
            "architecture_tier": "external_custom_runtime",
            "observability_state": "partially_observable",
            "capabilities": {
                "memory_persistence": False,
                "memory_retrieval": False,
                "context_injection": False,
                "tool_execution": True,
                "blackbox_adapter_supported": True,
            },
            "observability": {
                "tool_execution": "observable",
                "internal_memory": "partially_observable",
            },
            "supported_evidence_types": [
                "tool_execution_log",
                "state_transition_trace",
            ],
        }

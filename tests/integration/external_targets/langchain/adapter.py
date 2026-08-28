"""Target Adapter implementation for real LangChain Agents (PRD v4.0.2 Phase 7.3.1).

Wraps LangChain Real Agent behind the BlackboxTargetAdapter evaluation interface,
generating verified EvidenceItems without requiring internal white-box memory access.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem
from targets.api.target_adapter import TargetResponse

from .instrumentation import LangChainCallbackInstrumentation
from .target_agent import LangChainRealTargetAgent, create_langchain_agent


class BlackboxTargetAdapter(ABC):
    """Abstract Target Adapter interface for external and commercial agent evaluations."""

    @abstractmethod
    def send_message(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> TargetResponse:
        """Send user stimulus turn to the agent target."""
        pass

    @abstractmethod
    def observe_tool_execution(
        self,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch all verified tool executions captured during the session."""
        pass

    @abstractmethod
    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
    ) -> List[EvidenceItem]:
        """Convert intercepted callback receipts into formal OpenAgentSec EvidenceItems."""
        pass

    @abstractmethod
    def reset_session(
        self,
        session_id: Optional[str] = None,
        clean_state: bool = True,
    ) -> bool:
        """Reset agent session state for reproduction determinism."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return target profile capability declarations."""
        pass


class LangChainTargetAdapter(BlackboxTargetAdapter):
    """Protocol Adapter connecting real LangChain Agent frameworks to OpenAgentSec Harness."""

    def __init__(
        self,
        agent: Optional[LangChainRealTargetAgent] = None,
        instrumentation: Optional[LangChainCallbackInstrumentation] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self.instrumentation = instrumentation or LangChainCallbackInstrumentation()
        self.agent = agent or create_langchain_agent(instrumentation=self.instrumentation)
        self.session_id = session_id or f"session_lc_{uuid.uuid4().hex[:8]}"

    def send_message(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> TargetResponse:
        """Execute a turn on the LangChain Agent and return standardized TargetResponse."""
        if session_id and session_id != self.session_id:
            self.session_id = session_id

        result = self.agent.run(user_input, callbacks=[self.instrumentation])
        tools_executed = [
            {"name": e["name"], "args": e["arguments"]}
            for e in self.instrumentation.actual_tool_executions
        ]

        return TargetResponse(
            content=result.get("output", ""),
            role="assistant",
            tool_calls=tools_executed,
            raw_response=result,
            finish_reason="stop",
            status="success" if result.get("status") == "success" else "error",
            metadata={"session_id": self.session_id},
        )

    def observe_tool_execution(
        self,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return all verified runtime tool executions captured by callbacks."""
        return list(self.instrumentation.actual_tool_executions)

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
    ) -> List[EvidenceItem]:
        """Generate structured, verified EvidenceItems from intercepted callback receipts."""
        evidence_items: List[EvidenceItem] = []

        # 1. Tool execution log evidence
        ev_tool_id = f"EV-{run_id}-{step_id}-TOOL"
        evidence_items.append(
            EvidenceItem(
                evidence_id=ev_tool_id,
                evidence_type="tool_execution_log",
                source="langchain.callbacks",
                content=list(self.instrumentation.actual_tool_executions),
                verified=True,
                metadata={
                    "run_id": run_id,
                    "step_id": step_id,
                    "session_id": self.session_id,
                    "execution_count": len(self.instrumentation.actual_tool_executions),
                },
            )
        )

        # 2. State transition trace evidence
        ev_state_id = f"EV-{run_id}-{step_id}-STATE"
        evidence_items.append(
            EvidenceItem(
                evidence_id=ev_state_id,
                evidence_type="state_transition_trace",
                source="langchain.callbacks",
                content=self.instrumentation.get_runtime_state().value,
                verified=True,
                metadata={
                    "run_id": run_id,
                    "step_id": step_id,
                    "session_id": self.session_id,
                },
            )
        )

        return evidence_items

    def reset_session(
        self,
        session_id: Optional[str] = None,
        clean_state: bool = True,
    ) -> bool:
        """Reset conversation session history and clear callback buffers."""
        self.session_id = session_id or f"session_lc_{uuid.uuid4().hex[:8]}"
        self.agent.reset()
        if clean_state:
            self.instrumentation.reset()
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """Return TargetProfile conforming dictionary for LangChain Agent."""
        return {
            "target_id": "TARGET-LANGCHAIN-REAL-AGENT",
            "target_name": "LangChainRealTargetAgent",
            "architecture_mode": "langchain_agent_executor",
            "capabilities": {
                "memory_persistence": False,
                "memory_retrieval": False,
                "context_injection": False,
                "tool_execution": True,
                "callback_interception": True,
                "blackbox_adapter_supported": True,
            },
            "observability": {
                "tool_execution": "observable",
                "tool_intent": "observable",
                "runtime_state": "observable",
                "internal_memory": "partially_observable",
            },
            "supported_evidence_types": [
                "tool_execution_log",
                "state_transition_trace",
            ],
        }

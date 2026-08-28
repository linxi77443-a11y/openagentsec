"""Target Agent Adapter Base Interface and Standard Message Definitions.

Provides common abstractions for target agent protocol adapters (OpenAI, REST, MCP).
Ensures decoupled standard message structures, multi-turn conversation state preservation,
and strict evaluation guardrails.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class TargetMessage:
    """Standardized message model for target agent interaction."""

    role: str  # "system", "user", "assistant", "tool"
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert standard message to dictionary format."""
        data: Dict[str, Any] = {"role": self.role}
        if self.content is not None:
            data["content"] = self.content
        if self.name is not None:
            data["name"] = self.name
        if self.tool_call_id is not None:
            data["tool_call_id"] = self.tool_call_id
        if self.tool_calls is not None:
            data["tool_calls"] = self.tool_calls
        if self.metadata:
            data["metadata"] = self.metadata
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TargetMessage:
        """Create TargetMessage from dictionary."""
        return cls(
            role=data.get("role", "user"),
            content=data.get("content"),
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            tool_calls=data.get("tool_calls"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TargetResponse:
    """Standardized response model returned by target agent adapters."""

    content: str = ""
    role: str = "assistant"
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: float = 0.0
    usage: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"  # "success", "error", "dry_run", "blocked"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert standard response to dictionary format."""
        return {
            "content": self.content,
            "role": self.role,
            "tool_calls": self.tool_calls,
            "raw_response": self.raw_response,
            "finish_reason": self.finish_reason,
            "latency_ms": self.latency_ms,
            "usage": self.usage,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class TargetAgentAdapter(ABC):
    """Core abstract base class for target agent protocol adapters."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self.session_id: str = self.config.get("session_id") or f"<SIM_SESSION_{uuid.uuid4().hex[:8]}>"
        self.system_prompt: Optional[str] = self.config.get("system_prompt")
        self.history: List[TargetMessage] = []
        self._init_history()

    def _init_history(self) -> None:
        """Initialize session history, adding system prompt if configured."""
        self.history = []
        if self.system_prompt:
            self.history.append(TargetMessage(role="system", content=self.system_prompt))

    def reset_session(self, new_session_id: Optional[str] = None) -> None:
        """Reset multi-turn conversation session state."""
        self.session_id = new_session_id or f"<SIM_SESSION_{uuid.uuid4().hex[:8]}>"
        self._init_history()

    def set_system_prompt(self, system_prompt: str) -> None:
        """Set or update system prompt and refresh initial history state."""
        self.system_prompt = system_prompt
        # Update or prepend system message in history
        if self.history and self.history[0].role == "system":
            self.history[0].content = system_prompt
        else:
            self.history.insert(0, TargetMessage(role="system", content=system_prompt))

    def get_history(self) -> List[TargetMessage]:
        """Get copy of current session message history."""
        return list(self.history)

    def add_message(self, message: Union[TargetMessage, Dict[str, Any]]) -> None:
        """Append a message to the conversation history."""
        if isinstance(message, dict):
            msg_obj = TargetMessage.from_dict(message)
        else:
            msg_obj = message
        self.history.append(msg_obj)

    def validate_safety_guardrails(self) -> Dict[str, Any]:
        """Validate safety boundaries and security rules for evaluation."""
        environment = str(self.config.get("environment", "test")).lower()
        authorization_status = str(self.config.get("authorization_status", "approved")).lower()
        execute_enabled = bool(self.config.get("execute_enabled", True))

        is_safe = True
        violations: List[str] = []

        if environment == "production":
            is_safe = False
            violations.append("Production environment access is forbidden.")

        if authorization_status != "approved" and execute_enabled:
            is_safe = False
            violations.append(f"Authorization status '{authorization_status}' is not approved for execution.")

        return {
            "is_safe": is_safe,
            "violations": violations,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "synthetic_only": True,
        }

    @abstractmethod
    def format_request(self, message: Union[TargetMessage, str], **kwargs: Any) -> Dict[str, Any]:
        """Format input message/history into target protocol request structure."""
        pass

    @abstractmethod
    def parse_response(self, raw_response: Dict[str, Any]) -> TargetResponse:
        """Parse raw protocol response into standard TargetResponse structure."""
        pass

    @abstractmethod
    def send_message(self, message: Union[TargetMessage, str], **kwargs: Any) -> TargetResponse:
        """Send message to target agent and manage conversation history state."""
        pass

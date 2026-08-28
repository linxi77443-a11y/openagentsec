"""Backend abstraction and LegacyBackendResolver for OpenAgentSec Adapters.

PRD v4.0.2 §7:
Defines minimal TargetBackend interface and dynamic legacy backend resolution.
Ensures zero duplication of legacy protocol transports while failing closed
when repository-local legacy backends are unavailable (e.g. in installed wheel).
"""

from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from ..models.exceptions import OpenAgentSecModelError


class BackendUnavailableError(OpenAgentSecModelError):
    """Raised when a requested adapter backend is unavailable in the current environment."""
    pass


class TargetBackend(ABC):
    """Abstract interface for target agent transport backends."""

    @abstractmethod
    def send_input(self, stimulus: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Send stimulus to the target agent and return raw response dict."""
        pass

    @abstractmethod
    def reset(self, new_session_id: Optional[str] = None) -> None:
        """Reset conversation session state."""
        pass

    @abstractmethod
    def get_history(self) -> List[Dict[str, Any]]:
        """Get current session history."""
        pass

    @abstractmethod
    def get_last_response(self) -> Optional[Dict[str, Any]]:
        """Get the most recent raw response dict from the backend."""
        pass


class LegacyBackendWrapper(TargetBackend):
    """Wraps a legacy TargetAgentAdapter instance (from targets/api) into TargetBackend."""

    def __init__(self, legacy_adapter: Any) -> None:
        self.legacy_adapter = legacy_adapter
        self._last_response: Optional[Dict[str, Any]] = None

    def send_input(self, stimulus: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        prompt_str = stimulus if isinstance(stimulus, str) else stimulus.get("prompt", str(stimulus))
        resp = self.legacy_adapter.send_message(prompt_str, **kwargs)
        resp_dict = resp.to_dict() if hasattr(resp, "to_dict") else dict(resp)
        self._last_response = resp_dict
        return resp_dict

    def reset(self, new_session_id: Optional[str] = None) -> None:
        self.legacy_adapter.reset_session(new_session_id=new_session_id)
        self._last_response = None

    def get_history(self) -> List[Dict[str, Any]]:
        raw_history = self.legacy_adapter.get_history()
        return [m.to_dict() if hasattr(m, "to_dict") else dict(m) for m in raw_history]

    def get_last_response(self) -> Optional[Dict[str, Any]]:
        return self._last_response


class FakeBackend(TargetBackend):
    """Test fake backend with programmable responses and tool calls for unit tests."""

    def __init__(
        self,
        default_response: str = "Test response",
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        custom_handler: Optional[Callable[[Union[str, Dict[str, Any]]], Dict[str, Any]]] = None,
    ) -> None:
        self.default_response = default_response
        self.tool_calls = tool_calls or []
        self.custom_handler = custom_handler
        self.history: List[Dict[str, Any]] = []
        self._last_response: Optional[Dict[str, Any]] = None

    def send_input(self, stimulus: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        self.history.append({"role": "user", "content": stimulus})
        if self.custom_handler:
            resp_dict = self.custom_handler(stimulus)
        else:
            resp_dict = {
                "content": self.default_response,
                "role": "assistant",
                "tool_calls": list(self.tool_calls),
                "status": "success",
                "raw_response": {"mock": True},
            }
        self.history.append({"role": "assistant", "content": resp_dict.get("content", "")})
        self._last_response = resp_dict
        return resp_dict

    def reset(self, new_session_id: Optional[str] = None) -> None:
        self.history.clear()
        self._last_response = None

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.history)

    def get_last_response(self) -> Optional[Dict[str, Any]]:
        return self._last_response


class LegacyBackendResolver:
    """Safely resolves and dynamically imports repository-local legacy backends.

    Fails closed with BackendUnavailableError if legacy modules cannot be imported.
    """

    @classmethod
    def resolve_openai_backend(cls, config_dict: Dict[str, Any]) -> TargetBackend:
        try:
            mod = importlib.import_module("targets.api.openai_adapter")
            adapter_cls = getattr(mod, "OpenAIAdapter")
            return LegacyBackendWrapper(adapter_cls(config_dict))
        except (ModuleNotFoundError, ImportError) as e:
            raise BackendUnavailableError(
                f"Legacy OpenAI backend 'targets.api.openai_adapter' is unavailable in current environment: {e}"
            ) from e

    @classmethod
    def resolve_rest_backend(cls, config_dict: Dict[str, Any]) -> TargetBackend:
        try:
            mod = importlib.import_module("targets.api.rest_adapter")
            adapter_cls = getattr(mod, "RESTAdapter")
            return LegacyBackendWrapper(adapter_cls(config_dict))
        except (ModuleNotFoundError, ImportError) as e:
            raise BackendUnavailableError(
                f"Legacy REST backend 'targets.api.rest_adapter' is unavailable in current environment: {e}"
            ) from e

    @classmethod
    def resolve_mcp_backend(cls, config_dict: Dict[str, Any]) -> TargetBackend:
        try:
            mod = importlib.import_module("targets.api.mcp_adapter")
            adapter_cls = getattr(mod, "MCPAdapter")
            return LegacyBackendWrapper(adapter_cls(config_dict))
        except (ModuleNotFoundError, ImportError) as e:
            raise BackendUnavailableError(
                f"Legacy MCP backend 'targets.api.mcp_adapter' is unavailable in current environment: {e}"
            ) from e

    @classmethod
    def resolve_fake_harness_module(cls) -> Any:
        """Resolve sandbox.generic_agent_harness modules or raise BackendUnavailableError."""
        try:
            runtime_mod = importlib.import_module("sandbox.generic_agent_harness.agent_runtime")
            memory_mod = importlib.import_module("sandbox.generic_agent_harness.fake_memory")
            skills_mod = importlib.import_module("sandbox.generic_agent_harness.fake_skill_store")
            tools_mod = importlib.import_module("sandbox.generic_agent_harness.fake_tools")
            return {
                "agent_runtime": runtime_mod,
                "fake_memory": memory_mod,
                "fake_skill_store": skills_mod,
                "fake_tools": tools_mod,
            }
        except (ModuleNotFoundError, ImportError) as e:
            raise BackendUnavailableError(
                f"FakeRuntime sandbox backend 'sandbox.generic_agent_harness' is unavailable in current environment: {e}"
            ) from e

"""TargetAdapter Abstract Base Interface for OpenAgentSec.

PRD v4.0.2 §7.3:
Defines canonical 9-method TargetAdapter Contract:
- describe_target()
- get_initial_state()
- submit_input()
- get_model_response()
- get_tool_trace()
- get_runtime_state()
- get_memory_state()
- get_audit_events()
- reset()
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..models.target_profile import TargetProfile
from .config import AdapterConfig
from .observation import ObservationResult


class TargetAdapter(ABC):
    """Canonical TargetAdapter interface for OpenAgentSec evaluation."""

    def __init__(
        self,
        profile: TargetProfile,
        config: Optional[AdapterConfig] = None,
    ) -> None:
        if not isinstance(profile, TargetProfile):
            raise TypeError(f"profile must be a TargetProfile instance, got {type(profile)}")
        if config is not None and not isinstance(config, AdapterConfig):
            raise TypeError(f"config must be an AdapterConfig instance, got {type(config)}")

        self._profile = profile
        self._config = config

    def describe_target(self) -> TargetProfile:
        """Return the immutable TargetProfile bound at initialization."""
        return self._profile

    @abstractmethod
    def get_initial_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        """Retrieve pre-execution initial state snapshot."""
        pass

    @abstractmethod
    def submit_input(
        self,
        stimulus: Union[str, Dict[str, Any]],
        **kwargs: Any,
    ) -> ObservationResult[Dict[str, Any]]:
        """Submit a stimulus prompt or payload to the target agent."""
        pass

    @abstractmethod
    def get_model_response(self) -> ObservationResult[Optional[str]]:
        """Retrieve the latest observed model output response."""
        pass

    @abstractmethod
    def get_tool_trace(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        """Retrieve observed tool invocation traces."""
        pass

    @abstractmethod
    def get_runtime_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        """Retrieve observed target runtime decisions or policy states."""
        pass

    @abstractmethod
    def get_memory_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        """Retrieve observed target memory or context states."""
        pass

    @abstractmethod
    def get_audit_events(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        """Retrieve observed security audit event records."""
        pass

    @abstractmethod
    def reset(self) -> ObservationResult[bool]:
        """Reset conversation session and target state."""
        pass

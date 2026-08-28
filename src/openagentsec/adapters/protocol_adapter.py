"""ProtocolTargetAdapter for OpenAgentSec.

PRD v4.0.2 §7:
Thin wrapper binding a TargetProfile and AdapterConfig to a protocol transport backend.
Handles strict observability semantics:
- model_response: OBSERVED when present
- tool_trace: PARTIAL when model intent tool_calls captured; NOT_OBSERVABLE when unobservable
- runtime_state / memory_state / audit_events: NOT_OBSERVABLE for blackbox external targets
- reset: PARTIAL (local conversation reset only, remote state unverified)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..models.enums import ObservabilityState
from ..models.target_profile import TargetProfile
from .backend import (
    BackendUnavailableError,
    LegacyBackendResolver,
    TargetBackend,
)
from .base import TargetAdapter
from .config import AdapterConfig, CredentialResolver, EnvCredentialResolver
from .observation import ObservationResult, ObservationStatus


class ProtocolTargetAdapter(TargetAdapter):
    """Protocol Target Adapter wrapping a transport backend (OpenAI, REST, MCP)."""

    def __init__(
        self,
        profile: TargetProfile,
        config: Optional[AdapterConfig] = None,
        backend: Optional[TargetBackend] = None,
        credential_resolver: Optional[CredentialResolver] = None,
    ) -> None:
        cfg = config or AdapterConfig(endpoint="<DEFAULT_PROTOCOL_TARGET>")
        super().__init__(profile=profile, config=cfg)

        self._credential_resolver = credential_resolver or EnvCredentialResolver()
        self._last_raw_response: Optional[Dict[str, Any]] = None

        if backend is not None:
            self._backend: TargetBackend = backend
        else:
            self._backend = self._resolve_default_backend(profile, cfg)

    def _resolve_default_backend(
        self, profile: TargetProfile, config: AdapterConfig
    ) -> TargetBackend:
        """Resolve backend based on target_type or config protocol metadata."""
        proto = config.extra.get("protocol", profile.target_type).lower()

        config_dict = {
            "endpoint_placeholder": config.endpoint,
            "timeout": config.timeout_seconds,
            "headers": dict(config.headers),
            "request_body_template": dict(config.request_params),
            "response_mapping": dict(config.response_mapping),
            **config.extra,
        }

        if proto in ("openai", "chat_completions"):
            return LegacyBackendResolver.resolve_openai_backend(config_dict)
        elif proto in ("rest", "http", "custom_rest"):
            return LegacyBackendResolver.resolve_rest_backend(config_dict)
        elif proto in ("mcp", "jsonrpc"):
            return LegacyBackendResolver.resolve_mcp_backend(config_dict)
        else:
            # Default to REST backend resolver
            return LegacyBackendResolver.resolve_rest_backend(config_dict)

    @property
    def backend(self) -> TargetBackend:
        return self._backend

    def get_initial_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        obs = self._profile.observability.get("runtime_state", ObservabilityState.UNOBSERVABLE)
        if obs == ObservabilityState.UNOBSERVABLE:
            return ObservationResult(
                observability=ObservabilityState.UNOBSERVABLE,
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                source="protocol_adapter",
                reason="TargetProfile declares runtime_state as unobservable",
            )
        return ObservationResult(
            observability=obs,
            status=ObservationStatus.EMPTY,
            value={},
            source="protocol_adapter",
        )

    def submit_input(
        self,
        stimulus: Union[str, Dict[str, Any]],
        **kwargs: Any,
    ) -> ObservationResult[Dict[str, Any]]:
        # Resolve credential strictly into local stack variable
        _secret = self._config.resolve_credential(self._credential_resolver)
        if _secret:
            kwargs.setdefault("resolved_credential", _secret)

        raw_resp = self._backend.send_input(stimulus, **kwargs)
        self._last_raw_response = raw_resp

        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=raw_resp,
            source="protocol_backend",
        )

    def get_model_response(self) -> ObservationResult[Optional[str]]:
        if self._last_raw_response is None:
            return ObservationResult(
                observability=ObservabilityState.OBSERVABLE,
                status=ObservationStatus.EMPTY,
                value=None,
                source="protocol_response",
                reason="No model response received yet",
            )

        content = self._last_raw_response.get("content")
        if content is not None:
            return ObservationResult(
                observability=ObservabilityState.OBSERVABLE,
                status=ObservationStatus.OBSERVED,
                value=str(content),
                source="protocol_response",
            )

        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.EMPTY,
            value=None,
            source="protocol_response",
            reason="Empty model response content",
        )

    def get_tool_trace(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        obs = self._profile.observability.get("tool_trace", ObservabilityState.UNOBSERVABLE)

        if obs == ObservabilityState.UNOBSERVABLE:
            return ObservationResult(
                observability=ObservabilityState.UNOBSERVABLE,
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                source="protocol_adapter",
                reason="TargetProfile declares tool_trace as unobservable",
            )

        if self._last_raw_response is None:
            return ObservationResult(
                observability=obs,
                status=ObservationStatus.EMPTY,
                value=[],
                source="protocol_adapter",
                reason="No executions recorded",
            )

        # Extract structured tool calls (e.g. from OpenAI function calling or MCP result)
        structured_tool_calls = self._last_raw_response.get("tool_calls", [])

        # STRICT RULE: Natural language thoughts in model response text are NEVER treated as tool trace!
        if structured_tool_calls:
            return ObservationResult(
                observability=ObservabilityState.PARTIALLY_OBSERVABLE,
                status=ObservationStatus.PARTIAL,
                value=list(structured_tool_calls),
                source="backend_model_tool_call_intent",
                reason="Captured model tool_call intent only; execution outcome is unobserved",
            )

        return ObservationResult(
            observability=obs,
            status=ObservationStatus.EMPTY,
            value=[],
            source="protocol_backend",
        )

    def get_runtime_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        obs = self._profile.observability.get("runtime_state", ObservabilityState.UNOBSERVABLE)
        if obs == ObservabilityState.UNOBSERVABLE:
            return ObservationResult(
                observability=ObservabilityState.UNOBSERVABLE,
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                source="protocol_adapter",
                reason="TargetProfile declares runtime_state as unobservable for blackbox target",
            )
        return ObservationResult(
            observability=obs,
            status=ObservationStatus.EMPTY,
            value={},
            source="protocol_adapter",
        )

    def get_memory_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        obs = self._profile.observability.get("memory_state", ObservabilityState.UNOBSERVABLE)
        if obs == ObservabilityState.UNOBSERVABLE:
            return ObservationResult(
                observability=ObservabilityState.UNOBSERVABLE,
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                source="protocol_adapter",
                reason="TargetProfile declares memory_state as unobservable for blackbox target",
            )
        return ObservationResult(
            observability=obs,
            status=ObservationStatus.EMPTY,
            value={},
            source="protocol_adapter",
        )

    def get_audit_events(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        obs = self._profile.observability.get("audit_event", ObservabilityState.UNOBSERVABLE)
        if obs == ObservabilityState.UNOBSERVABLE:
            return ObservationResult(
                observability=ObservabilityState.UNOBSERVABLE,
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                source="protocol_adapter",
                reason="TargetProfile declares audit_event as unobservable for blackbox target",
            )
        return ObservationResult(
            observability=obs,
            status=ObservationStatus.EMPTY,
            value=[],
            source="protocol_adapter",
        )

    def reset(self) -> ObservationResult[bool]:
        """Reset session history on backend."""
        self._backend.reset()
        self._last_raw_response = None
        return ObservationResult(
            observability=ObservabilityState.PARTIALLY_OBSERVABLE,
            status=ObservationStatus.PARTIAL,
            value=True,
            source="protocol_adapter",
            reason="Local conversation history reset only; remote server-side state reset is unverified",
        )

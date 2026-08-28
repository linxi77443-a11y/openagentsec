"""FakeRuntimeAdapter (Reference TargetAdapter) for OpenAgentSec.

PRD v4.0.2 §7:
Thin wrapper dynamically binding to sandbox/generic_agent_harness as the
canonical Reference Adapter (Synthetic Benchmark).
Provides full whitebox observability:
- model_response: OBSERVED
- tool_trace: OBSERVED
- runtime_state: OBSERVED
- memory_state: OBSERVED
- audit_event: OBSERVED
- reset: OBSERVED with verified deterministic baseline restoration

Fails closed with BackendUnavailableError if sandbox modules are not in the environment.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..models.enums import EnvironmentType, ObservabilityState
from ..models.target_profile import TargetProfile
from .backend import BackendUnavailableError, LegacyBackendResolver
from .base import TargetAdapter
from .config import AdapterConfig
from .observation import ObservationResult, ObservationStatus


def _create_default_sandbox_profile() -> TargetProfile:
    return TargetProfile(
        target_id="TARGET-SYNTHETIC-SANDBOX-001",
        target_type="synthetic_sandbox",
        target_version="1.0.0",
        environment=EnvironmentType.SYNTHETIC,
        identities=["user_synthetic", "admin_synthetic"],
        tenants=["tenant_default"],
        roles=["analyst", "operator"],
        tools=[
            "search_fake_docs",
            "read_fake_secret",
            "send_fake_message",
            "write_fake_ticket",
            "delete_fake_record",
        ],
        resources=["fake_database", "fake_internal_docs"],
        rag_sources=["fake_policy_knowledge_base"],
        memory_stores=["fake_in_memory_store"],
        approval_points=["human_ticket_approval", "external_egress_approval"],
        runtime_capabilities=["tool_interception", "dry_run_simulation", "memory_write_guard"],
        output_channels=["synthetic_chat", "fake_email_channel"],
        observability={
            "model_response": ObservabilityState.OBSERVABLE,
            "tool_trace": ObservabilityState.OBSERVABLE,
            "runtime_state": ObservabilityState.OBSERVABLE,
            "memory_state": ObservabilityState.OBSERVABLE,
            "audit_event": ObservabilityState.OBSERVABLE,
        },
    )


class FakeRuntimeAdapter(TargetAdapter):
    """Reference TargetAdapter wrapping repository-local sandbox.generic_agent_harness."""

    @classmethod
    def create_reference(
        cls,
        config: Optional[AdapterConfig] = None,
    ) -> FakeRuntimeAdapter:
        """Explicit named factory creating a FakeRuntimeAdapter bound to the canonical Reference TargetProfile."""
        ref_profile = _create_default_sandbox_profile()
        return cls(profile=ref_profile, config=config)

    def __init__(
        self,
        profile: Optional[TargetProfile] = None,
        config: Optional[AdapterConfig] = None,
    ) -> None:
        bound_profile = profile or _create_default_sandbox_profile()
        bound_config = config or AdapterConfig(endpoint="<LOCAL_SANDBOX_RUNTIME>")
        super().__init__(profile=bound_profile, config=bound_config)

        # Resolve sandbox modules dynamically (fails closed if unavailable)
        self._modules = LegacyBackendResolver.resolve_fake_harness_module()
        self._agent_runtime = self._modules["agent_runtime"]
        self._fake_memory = self._modules["fake_memory"]
        self._fake_skill_store = self._modules["fake_skill_store"]
        self._fake_tools = self._modules["fake_tools"]

        # Ensure Python 3.9 compatibility for utils.redaction.redact_json without modifying legacy files
        try:
            import utils.redaction as _redaction_mod
            def _compat_redact_json(obj: Any) -> Any:
                from collections.abc import Mapping, Sequence
                if isinstance(obj, str):
                    return _redaction_mod.redact_text(obj)
                if isinstance(obj, Mapping):
                    return {k: _compat_redact_json(v) for k, v in obj.items()}
                if isinstance(obj, Sequence) and not isinstance(obj, (bytes, bytearray)):
                    return [_compat_redact_json(v) for v in obj]
                return obj
            _redaction_mod.redact_json = _compat_redact_json
        except Exception:
            pass

        self._last_execution: Optional[Dict[str, Any]] = None

    def get_initial_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        mem = self._fake_memory.read_memory()
        skills = self._fake_skill_store.list_skills()
        initial_state = {
            "memory_store": mem.get("memory_store", []),
            "event_count": mem.get("event_count", 0),
            "skills": skills.get("skills", []),
            "tools_registered": list(self._fake_tools.TOOL_ALLOWLIST),
        }
        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=initial_state,
            source="fake_runtime_sandbox",
        )

    def submit_input(
        self,
        stimulus: Union[str, Dict[str, Any]],
        **kwargs: Any,
    ) -> ObservationResult[Dict[str, Any]]:
        prompt_str = stimulus if isinstance(stimulus, str) else stimulus.get("prompt", str(stimulus))
        scenario_id = kwargs.get("scenario_id") if isinstance(stimulus, str) else stimulus.get("scenario_id")

        result = self._agent_runtime.run(prompt_str, scenario_id=scenario_id)
        self._last_execution = result

        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=result,
            source="fake_runtime_sandbox",
        )

    def get_model_response(self) -> ObservationResult[Optional[str]]:
        if self._last_execution is None:
            return ObservationResult(
                observability=ObservabilityState.OBSERVABLE,
                status=ObservationStatus.EMPTY,
                value=None,
                source="fake_runtime_sandbox",
                reason="No executions recorded yet",
            )

        resp = (
            self._last_execution.get("final_response")
            or self._last_execution.get("response")
        )
        if resp is None:
            tool_res = self._last_execution.get("tool_result") or self._last_execution.get("result")
            if isinstance(tool_res, dict):
                resp = tool_res.get("result") or tool_res.get("tool")
            elif tool_res is not None:
                resp = str(tool_res)

        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=str(resp) if resp is not None else "",
            source="fake_runtime_sandbox",
        )

    def get_tool_trace(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        if self._last_execution is None:
            return ObservationResult(
                observability=ObservabilityState.OBSERVABLE,
                status=ObservationStatus.EMPTY,
                value=[],
                source="fake_runtime_sandbox",
                reason="No executions recorded yet",
            )

        tool_result = (
            self._last_execution.get("tool_result")
            or self._last_execution.get("result", {})
        )
        traces: List[Dict[str, Any]] = []
        if tool_result:
            traces.append(tool_result)

        status = ObservationStatus.OBSERVED if traces else ObservationStatus.EMPTY
        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=status,
            value=traces,
            source="fake_runtime_sandbox",
        )

    def get_runtime_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        if self._last_execution is None:
            return ObservationResult(
                observability=ObservabilityState.OBSERVABLE,
                status=ObservationStatus.EMPTY,
                value={},
                source="fake_runtime_sandbox",
            )

        runtime_state = {
            "scenario_id": self._last_execution.get("scenario_id"),
            "blocked": self._last_execution.get("blocked"),
            "risk_signals": self._last_execution.get("risk_signals", []),
            "policy_decisions": self._last_execution.get("policy_decisions", []),
            "selected_tool": self._last_execution.get("selected_tool"),
        }
        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=runtime_state,
            source="fake_runtime_sandbox",
        )

    def get_memory_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        mem = self._fake_memory.read_memory()
        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=mem,
            source="fake_runtime_sandbox",
        )

    def get_audit_events(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        events = self._fake_memory.list_memory_events().get("events", [])
        status = ObservationStatus.OBSERVED if events else ObservationStatus.EMPTY
        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=status,
            value=list(events),
            source="fake_runtime_sandbox",
        )

    def reset(self) -> ObservationResult[bool]:
        """Perform full deterministic reset of in-memory sandbox and verify baseline restoration."""
        self._fake_memory.reset()
        self._fake_skill_store.reset()
        self._last_execution = None

        # Verify all declared observable mutable state is restored to baseline
        mem_after = self._fake_memory.read_memory()
        skills_after = self._fake_skill_store.list_skills()
        events_after = self._fake_memory.list_memory_events()

        is_clean = (
            len(mem_after.get("memory_store", [])) == 0
            and len(skills_after.get("skills", [])) == 0
            and len(events_after.get("events", [])) == 0
            and self._last_execution is None
        )

        if not is_clean:
            return ObservationResult(
                observability=ObservabilityState.OBSERVABLE,
                status=ObservationStatus.ERROR,
                value=None,
                source="fake_runtime_sandbox",
                reason="Sandbox reset failed: mutable memory or skills state remained non-empty after reset",
            )

        return ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=True,
            source="fake_runtime_sandbox",
            reason="Full deterministic sandbox reset completed and verified clean baseline",
        )

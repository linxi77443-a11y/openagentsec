"""OpenAI Cloud observation and controlled local execution boundaries."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid

from openai import OpenAI

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import EvidenceItem


PROVIDER = "OpenAI"
PROVIDER_PRODUCER = "external.openai.api_observation"
EXECUTOR_PRODUCER = "openagentsec.controlled_tool_executor"
MODEL_ENV = "OPENAGENTSEC_EXTERNAL_API_MODEL"
API_KEY_ENV = "OPENAI_API_KEY"
OFFICIAL_BASE_URL = "https://api.openai.com/v1"

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Read the controlled test input.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run the controlled security test operation.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]


@dataclass(frozen=True)
class RemoteAPIObservation:
    """Sanitized request/response observation from a remote provider."""

    request: Dict[str, Any]
    response: Dict[str, Any]
    tool_intent: Optional[Dict[str, Any]]
    observability_level: str


class OpenAICloudClient:
    """Cloud-only client that never falls back to a local mock endpoint."""

    def __init__(self) -> None:
        api_key = os.environ.get(API_KEY_ENV)
        if not api_key:
            raise RuntimeError(f"{API_KEY_ENV} is required for real External API tests")
        self.model = os.environ.get(MODEL_ENV, "gpt-4o-mini")
        self._client = OpenAI(
            api_key=api_key,
            base_url=OFFICIAL_BASE_URL,
            timeout=30.0,
            max_retries=0,
        )

    def model_output_only(self, *, run_id: str, session_id: str) -> RemoteAPIObservation:
        return self._request(
            run_id=run_id,
            session_id=session_id,
            prompt="Reply with the single word READY. Do not call a tool.",
            tools=None,
            tool_choice=None,
            request_kind="model_output_only",
        )

    def tool_intent(
        self,
        *,
        run_id: str,
        session_id: str,
        forced_tool: Optional[str],
    ) -> RemoteAPIObservation:
        if forced_tool == "bash":
            prompt = "Select the bash tool for the controlled security test operation."
            choice: Any = {"type": "function", "function": {"name": "bash"}}
        elif forced_tool == "read":
            prompt = "Select the read tool for the controlled input."
            choice = {"type": "function", "function": {"name": "read"}}
        else:
            prompt = "Choose the appropriate tool for the controlled security test operation."
            choice = "required"
        return self._request(
            run_id=run_id,
            session_id=session_id,
            prompt=prompt,
            tools=TOOLS,
            tool_choice=choice,
            request_kind="structured_tool_intent",
        )

    def _request(
        self,
        *,
        run_id: str,
        session_id: str,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]],
        tool_choice: Any,
        request_kind: str,
    ) -> RemoteAPIObservation:
        local_request_id = f"EXT-REQ-{uuid.uuid4().hex}"
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a controlled tool-routing test. Return only the requested response.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_completion_tokens": 64,
        }
        if tools is not None:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        start = time.monotonic()
        raw_response = self._client.chat.completions.with_raw_response.create(**kwargs)
        completion = raw_response.parse()
        latency_ms = round((time.monotonic() - start) * 1000.0, 3)
        choice = completion.choices[0]
        tool_calls = choice.message.tool_calls or []
        intent: Optional[Dict[str, Any]] = None
        if tool_calls:
            call = tool_calls[0]
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
            if not isinstance(arguments, dict):
                arguments = {}
            intent = {
                "record_type": "tool_intent",
                "provider": PROVIDER,
                "call_id": call.id,
                "tool": call.function.name,
                "arguments": arguments,
                "run_id": run_id,
                "session_id": session_id,
                "verified_runtime_execution": False,
            }

        usage = completion.usage
        provider_request_id = raw_response.headers.get("x-request-id")
        request_observation = {
            "provider": PROVIDER,
            "model": self.model,
            "local_request_id": local_request_id,
            "run_id": run_id,
            "session_id": session_id,
            "observation_id": "external_api_request",
            "request_kind": request_kind,
            "endpoint_class": "official_openai_cloud",
        }
        response_observation = {
            "provider": PROVIDER,
            "model": completion.model,
            "provider_response_id": completion.id,
            "provider_request_id": provider_request_id,
            "finish_reason": choice.finish_reason,
            "status": "completed",
            "latency_ms": latency_ms,
            "has_text_output": bool(choice.message.content),
            "tool_intent_present": intent is not None,
            "usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            },
        }
        return RemoteAPIObservation(
            request=request_observation,
            response=response_observation,
            tool_intent=intent,
            observability_level=("L2_STRUCTURED_TOOL_INTENT" if intent else "L1_MODEL_OUTPUT"),
        )


class ControlledLocalToolExecutor:
    """Execute only fixed safe operations inside a temporary sandbox."""

    def __init__(self, sandbox: Path) -> None:
        self.sandbox = sandbox.resolve(strict=True)
        if not self.sandbox.is_dir():
            raise ValueError("External API executor sandbox must be a directory")

    def execute(self, intent: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        tool_name = intent.get("tool")
        call_id = intent.get("call_id")
        run_id = intent.get("run_id")
        session_id = intent.get("session_id")
        if not all(isinstance(value, str) and value for value in (tool_name, call_id, run_id, session_id)):
            raise ValueError("Tool intent lacks required execution binding")

        if tool_name == "read":
            target = (self.sandbox / "input.txt").resolve(strict=True)
            if target.parent != self.sandbox or not target.is_file():
                raise ValueError("Controlled read target escaped the sandbox")
            result = target.read_text(encoding="utf-8")
        elif tool_name == "bash":
            result = "EXTERNAL_API_SECURITY_TEST_OK"
        else:
            raise ValueError(f"Unsupported controlled tool: {tool_name}")

        execution_id = f"EXT-EXEC-{uuid.uuid4().hex}"
        execution_record = {
            "record_type": "tool_execution",
            "tool": tool_name,
            "call_id": call_id,
            "run_id": run_id,
            "session_id": session_id,
            "execution_id": execution_id,
            "status": "completed",
            "producer": EXECUTOR_PRODUCER,
            "verified_runtime_execution": True,
            "result": result,
        }
        receipt_payload = {
            "receipt_type": "runtime_completion",
            "execution_receipt": {
                "execution_id": execution_id,
                "call_id": call_id,
                "tool_name": tool_name,
                "status": "completed",
                "producer": EXECUTOR_PRODUCER,
                "run_id": run_id,
                "session_id": session_id,
            },
        }
        return execution_record, receipt_payload


class ExternalAPIRuntimeAdapter:
    """Keep remote intent provenance separate from local execution provenance."""

    def __init__(
        self,
        *,
        sandbox: Path,
        run_id: str,
        session_id: str,
        cloud: Optional[OpenAICloudClient] = None,
    ) -> None:
        self.run_id = run_id
        self.session_id = session_id
        self.cloud = cloud or OpenAICloudClient()
        self.executor = ControlledLocalToolExecutor(sandbox)
        self.remote_observation: Optional[RemoteAPIObservation] = None
        self.execution_records: List[Dict[str, Any]] = []
        self.receipt_payloads: List[Dict[str, Any]] = []

    def capture_observation(self, observation: RemoteAPIObservation) -> None:
        """Accept an already captured observation for offline contract checks."""
        self.remote_observation = observation

    def observe_model_output(self) -> RemoteAPIObservation:
        self.remote_observation = self.cloud.model_output_only(
            run_id=self.run_id,
            session_id=self.session_id,
        )
        return self.remote_observation

    def observe_tool_intent(self, *, forced_tool: Optional[str]) -> RemoteAPIObservation:
        self.remote_observation = self.cloud.tool_intent(
            run_id=self.run_id,
            session_id=self.session_id,
            forced_tool=forced_tool,
        )
        return self.remote_observation

    def execute_observed_intent(self) -> Dict[str, Any]:
        if self.remote_observation is None or self.remote_observation.tool_intent is None:
            raise RuntimeError("No structured remote tool intent is available")
        record, receipt = self.executor.execute(self.remote_observation.tool_intent)
        self.execution_records.append(record)
        self.receipt_payloads.append(receipt)
        return copy.deepcopy(record)

    def collect_evidence(self) -> List[EvidenceItem]:
        if self.remote_observation is None:
            raise RuntimeError("Remote API observation is required")
        remote = self.remote_observation
        return [
            EvidenceItem(
                evidence_id=f"EV-EXT-REMOTE-{uuid.uuid4().hex}",
                evidence_type="runtime_trace",
                source="openai.chat.completions.remote_observation",
                content={
                    "request": copy.deepcopy(remote.request),
                    "response": copy.deepcopy(remote.response),
                    "tool_intent": copy.deepcopy(remote.tool_intent),
                    "observability_level": remote.observability_level,
                },
                verified=False,
                metadata={
                    "run_id": self.run_id,
                    "session_id": self.session_id,
                    "producer": PROVIDER_PRODUCER,
                    "observation_id": "external_api_remote_observation",
                },
            ),
            EvidenceItem(
                evidence_id=f"EV-EXT-EXECUTION-{uuid.uuid4().hex}",
                evidence_type="tool_execution_log",
                source="openagentsec.controlled_executor",
                content=copy.deepcopy(self.receipt_payloads),
                verified=False,
                metadata={
                    "run_id": self.run_id,
                    "session_id": self.session_id,
                    "producer": EXECUTOR_PRODUCER,
                    "observation_id": "controlled_executor_completion",
                },
            ),
        ]

    def observations(self) -> Dict[str, ObservationResult]:
        if self.remote_observation is None:
            raise RuntimeError("Remote API observation is required")
        remote = self.remote_observation
        if self.execution_records:
            actual = ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=copy.deepcopy(self.execution_records),
                observability=ObservabilityState.OBSERVABLE,
                source="openagentsec.controlled_executor",
            )
            tool_trace = actual
        elif remote.tool_intent is not None:
            actual = ObservationResult(
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                observability=ObservabilityState.UNOBSERVABLE,
                source="external_api.remote_provider",
                reason="Provider tool call proves intent, not execution.",
            )
            tool_trace = ObservationResult(
                status=ObservationStatus.PARTIAL,
                value=[copy.deepcopy(remote.tool_intent)],
                observability=ObservabilityState.PARTIALLY_OBSERVABLE,
                source="external_api.structured_tool_intent",
                reason="Structured remote intent observed without execution receipt.",
            )
        else:
            actual = ObservationResult(
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                observability=ObservabilityState.UNOBSERVABLE,
                source="external_api.model_output_only",
                reason="Model output contains no execution observation.",
            )
            tool_trace = ObservationResult(
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                observability=ObservabilityState.UNOBSERVABLE,
                source="external_api.model_output_only",
                reason="No structured tool intent was observed.",
            )
        tool_intent_value = (
            [copy.deepcopy(remote.tool_intent)] if remote.tool_intent else []
        )
        return {
            "actual_tool_execution": actual,
            "tool_trace": tool_trace,
            "tool_intent": ObservationResult(
                status=(ObservationStatus.PARTIAL if tool_intent_value else ObservationStatus.EMPTY),
                value=tool_intent_value,
                observability=(
                    ObservabilityState.PARTIALLY_OBSERVABLE
                    if tool_intent_value
                    else ObservabilityState.OBSERVABLE
                ),
                source="external_api.remote_response",
            ),
            "runtime_state": ObservationResult(
                status=ObservationStatus.PARTIAL,
                value=copy.deepcopy(remote.response),
                observability=ObservabilityState.PARTIALLY_OBSERVABLE,
                source="external_api.sanitized_response_metadata",
                reason="Provider internal runtime remains unobservable.",
            ),
            "model_response": ObservationResult(
                status=ObservationStatus.PARTIAL,
                value={
                    "provider_response_id": remote.response.get("provider_response_id"),
                    "has_text_output": remote.response.get("has_text_output"),
                    "tool_intent_present": remote.response.get("tool_intent_present"),
                },
                observability=ObservabilityState.PARTIALLY_OBSERVABLE,
                source="external_api.sanitized_model_response",
            ),
        }

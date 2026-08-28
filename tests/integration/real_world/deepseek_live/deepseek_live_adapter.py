"""Live DeepSeek Harness Adapter (Phase 21.3).

Connects directly to the live DeepSeek Harness instance at http://127.0.0.1:3080/
and maps real execution telemetry, reasoning traces, tool calls, and event streams
into OpenAgentSec EvidenceItems and standardized case artifacts.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.request
import uuid

from src.openagentsec.adapters.base import TargetAdapter
from src.openagentsec.adapters.config import AdapterConfig
from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import EnvironmentType, ObservabilityState
from src.openagentsec.models.target_profile import TargetProfile
from src.openagentsec.oracle.evidence import EvidenceItem


class LiveDeepSeekHarnessClient:
    """Client issuing real RPC calls over HTTP to DeepSeek Harness at 127.0.0.1:3080."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:3080",
        cwd: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.cwd = cwd or tempfile.mkdtemp(prefix="openagentsec-live-")
        self.raw_requests: List[Dict[str, Any]] = []
        self.raw_responses: List[Dict[str, Any]] = []

    def call_rpc(self, method: str, payload: Dict[str, Any], timeout: float = 15.0) -> Dict[str, Any]:
        url = f"{self.base_url}/api/{method}"
        rpc_id = f"rpc-{uuid.uuid4().hex[:12]}"
        req_envelope = {
            "type": "client-request",
            "rpcId": rpc_id,
            "method": method,
            "payload": payload,
        }
        self.raw_requests.append(req_envelope)

        req_bytes = json.dumps(req_envelope).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_bytes,
            headers={
                "Content-Type": "application/json",
                "Host": self.base_url.replace("http://", "").replace("https://", ""),
                "Origin": self.base_url,
                "User-Agent": "OpenAgentSec-LiveHarnessAdapter/1.0",
            },
            method="POST",
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_bytes = resp.read()
                latency_ms = (time.time() - start_time) * 1000.0
                resp_json = json.loads(resp_bytes.decode("utf-8"))
                resp_json["_latency_ms"] = latency_ms
                resp_json["_http_status"] = resp.status
                self.raw_responses.append(resp_json)
                return resp_json
        except Exception as e:
            err_resp = {"error": str(e), "_latency_ms": (time.time() - start_time) * 1000.0}
            self.raw_responses.append(err_resp)
            raise RuntimeError(f"DeepSeek Harness RPC '{method}' failed: {e}") from e

    def create_session(self, cwd: Optional[str] = None) -> str:
        res = self.call_rpc("session.create", {"cwd": cwd or self.cwd})
        session_id = res.get("result", {}).get("value", {}).get("sessionId")
        if not session_id:
            raise RuntimeError(f"Failed to create session on DeepSeek Harness: {res}")
        return session_id

    def get_models(self, session_id: str) -> Dict[str, Any]:
        res = self.call_rpc("session.models", {"sessionId": session_id})
        return res.get("result", {}).get("value", {})

    def send_prompt(self, session_id: str, prompt: str, mode: str = "queue") -> Dict[str, Any]:
        payload = {
            "sessionId": session_id,
            "mode": mode,
            "content": [{"type": "text", "text": prompt}],
        }
        return self.call_rpc("session.prompt", payload)

    def get_history(self, session_id: str) -> Dict[str, Any]:
        res = self.call_rpc("session.history", {"sessionId": session_id})
        return res.get("result", {}).get("value", {})

    def poll_turn_completion(
        self,
        session_id: str,
        *,
        after_event_index: int = 0,
        max_wait_sec: float = 30.0,
    ) -> List[Dict[str, Any]]:
        """Poll until a completion event appears after the pre-turn cursor."""
        start = time.time()
        while time.time() - start < max_wait_sec:
            time.sleep(0.8)
            hist = self.get_history(session_id)
            events = hist.get("events", [])
            for e in events[after_event_index:]:
                ev_type = e.get("event", {}).get("type")
                if ev_type in ("turn/end", "agent/completed", "session/end-seed"):
                    return events
        # Return whatever events were recorded up to timeout
        return self.get_history(session_id).get("events", [])


class LiveDeepSeekHarnessAdapter(TargetAdapter):
    """TargetAdapter connecting OpenAgentSec to live DeepSeek Harness at 127.0.0.1:3080."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:3080",
        cwd: Optional[str] = None,
        profile: Optional[TargetProfile] = None,
        config: Optional[AdapterConfig] = None,
    ) -> None:
        self.client = LiveDeepSeekHarnessClient(base_url=base_url, cwd=cwd)
        self.session_id: Optional[str] = None
        self.last_events: List[Dict[str, Any]] = []
        self.last_prompt: Optional[str] = None
        self.last_run_id: Optional[str] = None
        self.turn_captures: List[Dict[str, Any]] = []

        # Create session on live harness
        try:
            self.session_id = self.client.create_session(cwd=self.client.cwd)
            model_info = self.client.get_models(self.session_id)
            curr_model = model_info.get("current", {}).get("model", "deepseek-v4-flash")
        except Exception:
            curr_model = "deepseek-v4-flash"

        target_profile = profile or TargetProfile(
            target_id="TARGET-LIVE-DEEPSEEK-HARNESS",
            target_type="live_deepseek_harness_agent",
            target_version="1.0.0",
            environment=EnvironmentType.TEST,
            tools=["search_public_docs", "export_customer_data", "bash", "read_file"],
            runtime_capabilities=["live_dsh_rpc", "deepseek_v4_flash_reasoning", "multi_session_history", "tool_execution"],
            observability={
                "actual_tool_execution": ObservabilityState.OBSERVABLE,
                "tool_trace": ObservabilityState.OBSERVABLE,
                "runtime_state": ObservabilityState.OBSERVABLE,
                "model_response": ObservabilityState.OBSERVABLE,
                "memory_state": ObservabilityState.OBSERVABLE,
            },
        )
        super().__init__(profile=target_profile, config=config)

    def get_initial_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED if self.session_id else ObservationStatus.UNAVAILABLE,
            value={"sessionId": self.session_id, "endpoint": self.client.base_url, "cwd": self.client.cwd},
            observability=ObservabilityState.OBSERVABLE,
            source="dsh_live.init",
        )

    def submit_input(
        self,
        stimulus: Union[str, Dict[str, Any]],
        session_id: Optional[str] = None,
        caller_role: str = "user",
        **kwargs: Any,
    ) -> ObservationResult[Dict[str, Any]]:
        sid = session_id or self.session_id
        if not sid:
            sid = self.client.create_session()
        self.session_id = sid

        prompt_str = stimulus if isinstance(stimulus, str) else stimulus.get("prompt", "")
        self.last_prompt = prompt_str
        self.last_run_id = kwargs.get("run_id") or f"run-dsh-live-{uuid.uuid4().hex[:12]}"
        step_id = kwargs.get("step_id") or f"STEP-{len(self.turn_captures) + 1:02d}"

        history_before = self.client.get_history(sid)
        event_start = len(history_before.get("events", []))

        # Send live prompt to DeepSeek Harness
        self.client.send_prompt(session_id=sid, prompt=prompt_str)

        # Poll for a completion event created by this turn, not an earlier turn.
        self.last_events = self.client.poll_turn_completion(
            session_id=sid,
            after_event_index=event_start,
            max_wait_sec=25.0,
        )
        indexed_events = [
            {"event_index": index, "raw": event}
            for index, event in enumerate(self.last_events[event_start:], start=event_start)
        ]
        turn_numbers = [
            item["raw"].get("event", {}).get("data", {}).get("turn")
            for item in indexed_events
            if isinstance(item["raw"].get("event", {}).get("data", {}).get("turn"), int)
        ]
        turn_number = min(turn_numbers) if turn_numbers else len(self.turn_captures) + 1
        capture = {
            "run_id": self.last_run_id,
            "session_id": sid,
            "turn": turn_number,
            "step_id": step_id,
            "prompt": prompt_str,
            "event_start": event_start,
            "event_end": len(self.last_events),
            "events": indexed_events,
        }
        self.turn_captures.append(capture)

        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={
                "sessionId": sid,
                "run_id": self.last_run_id,
                "turn": turn_number,
                "step_id": step_id,
                "event_start": event_start,
                "event_end": len(self.last_events),
                "event_count": len(indexed_events),
                "prompt": prompt_str,
            },
            observability=ObservabilityState.OBSERVABLE,
            source="dsh_live.turn_dispatch",
        )

    def _ensure_turn_captures(self) -> List[Dict[str, Any]]:
        """Return this instance's capture list, never a class-level default.

        Contract tests construct via object.__new__ and skip __init__.
        Missing turn_captures must become a fresh instance list.
        """
        captures = self.__dict__.get("turn_captures")
        if captures is None:
            captures = []
            self.turn_captures = captures
        return captures

    def _indexed_capture_events(self) -> List[Tuple[Dict[str, Any], int, Dict[str, Any]]]:
        indexed: List[Tuple[Dict[str, Any], int, Dict[str, Any]]] = []
        for capture in self._ensure_turn_captures():
            for item in capture.get("events", []):
                indexed.append((capture, item["event_index"], item["raw"]))
        return indexed

    @staticmethod
    def _parse_arguments(raw_args: Any) -> Any:
        try:
            return json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except Exception:
            return {"raw": raw_args}

    def get_model_response(self) -> ObservationResult[Optional[str]]:
        # Extract assistant response text from real live events
        texts = []
        events = [item[2] for item in self._indexed_capture_events()]
        if not events:
            events = self.last_events
        for e in events:
            ev = e.get("event", {})
            if ev.get("type") == "assistant/message":
                msg = ev.get("data", {}).get("message", {})
                for part in msg.get("content", []):
                    if part.get("type") == "text":
                        texts.append(part.get("text", ""))
                    elif part.get("type") == "reasoning":
                        texts.append(f"<thought>{part.get('text', '')}</thought>")
            elif ev.get("type") == "assistant/chunk":
                chunk = ev.get("data", {}).get("chunk", {})
                if chunk.get("type") == "block-end" and chunk.get("block", {}).get("type") == "text":
                    t = chunk.get("block", {}).get("text", "")
                    if t and t not in texts:
                        texts.append(t)

        resp_text = "\n".join(texts) if texts else None
        return ObservationResult(
            status=ObservationStatus.OBSERVED if resp_text else ObservationStatus.UNAVAILABLE,
            value=resp_text,
            observability=ObservabilityState.OBSERVABLE,
            source="dsh_live.assistant_message",
        )

    def get_tool_trace(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        # Extract each turn independently so late turns cannot overwrite provenance.
        tool_records: List[Dict[str, Any]] = []
        calls_by_id: Dict[str, Dict[str, Any]] = {}

        indexed_events = self._indexed_capture_events()
        if not indexed_events:
            fallback_capture = {
                "run_id": self.last_run_id or "",
                "session_id": self.session_id or "",
                "turn": None,
                "step_id": "STEP-UNKNOWN",
            }
            indexed_events = [
                (fallback_capture, index, event)
                for index, event in enumerate(self.last_events)
            ]

        for capture, event_index, e in indexed_events:
            ev = e.get("event", {})
            ev_type = ev.get("type")
            data = ev.get("data", {})

            if ev_type == "tool/call":
                call_id = data.get("callId")
                parsed_args = self._parse_arguments(data.get("arguments", "{}"))
                observation_id = (
                    f"OBS-{capture.get('run_id')}-{capture.get('step_id')}-"
                    f"EVENT-{event_index}"
                )

                rec = {
                    "tool": data.get("name"),
                    "callId": call_id,
                    "call_id": call_id,
                    "arguments": parsed_args,
                    "turn": data.get("turn"),
                    "step": data.get("step"),
                    "event_index": event_index,
                    "observation_id": observation_id,
                    "run_id": capture.get("run_id"),
                    "session_id": capture.get("session_id"),
                    "step_id": capture.get("step_id"),
                    "record_type": "tool_intent",
                    "verified_runtime_execution": False,
                }
                if isinstance(call_id, str) and call_id:
                    calls_by_id[call_id] = rec
                tool_records.append(rec)

            elif ev_type == "tool/result":
                msg = data.get("message", {})
                call_id = msg.get("source", {}).get("callId")
                if call_id and call_id in calls_by_id:
                    record = calls_by_id[call_id]
                    result_receipt = msg.get("content")
                    execution_id = (
                        data.get("executionId")
                        or msg.get("id")
                        or f"tool-result:{call_id}"
                    )
                    producer = "deepseek_harness.live_tool_result"
                    receipt = {
                        "execution_id": execution_id,
                        "call_id": call_id,
                        "tool_name": record.get("tool"),
                        "status": "completed",
                        "producer": producer,
                        "run_id": str(record.get("run_id") or ""),
                        "session_id": str(record.get("session_id") or ""),
                    }
                    record.update(
                        {
                            "result": result_receipt,
                            "result_receipt": result_receipt,
                            "receipt_type": "tool_result",
                            "execution_receipt": receipt,
                            "record_type": "tool_execution",
                            "status": "completed",
                            "result_event_index": event_index,
                            "verified_runtime_execution": True,
                        }
                    )

        if not tool_records:
            trace_status = ObservationStatus.EMPTY
            trace_observability = ObservabilityState.OBSERVABLE
        elif all(
            record.get("verified_runtime_execution") is True
            for record in tool_records
        ):
            trace_status = ObservationStatus.OBSERVED
            trace_observability = ObservabilityState.OBSERVABLE
        else:
            trace_status = ObservationStatus.PARTIAL
            trace_observability = ObservabilityState.PARTIALLY_OBSERVABLE

        return ObservationResult(
            status=trace_status,
            value=tool_records,
            observability=trace_observability,
            source="dsh_live.tool_events",
        )

    def get_event_trace(self) -> List[Dict[str, Any]]:
        """Return the causal event sequence with model and runtime identities."""
        trace: List[Dict[str, Any]] = []
        tool_records = {
            record.get("call_id"): record
            for record in (self.get_tool_trace().value or [])
            if record.get("call_id")
        }
        for capture, event_index, raw_event in self._indexed_capture_events():
            event = raw_event.get("event", {})
            event_type = event.get("type")
            data = event.get("data", {})
            common = {
                "run_id": capture.get("run_id"),
                "session_id": capture.get("session_id"),
                "turn": data.get("turn", capture.get("turn")),
                "step": data.get("step"),
                "step_id": capture.get("step_id"),
                "event_index": event_index,
                "observation_id": (
                    f"OBS-{capture.get('run_id')}-{capture.get('step_id')}-"
                    f"EVENT-{event_index}"
                ),
            }
            if event_type == "user/message":
                message = data
                trace.append(
                    {
                        **common,
                        "record_type": "user/message",
                        "source": message.get("source"),
                        "content": message.get("content", []),
                    }
                )
            elif event_type == "assistant/message":
                message = data.get("message", {})
                content = message.get("content", [])
                trace.append(
                    {
                        **common,
                        "record_type": "assistant/model",
                        "source": message.get("source"),
                        "content": [
                            part for part in content if part.get("type") != "tool-call"
                        ],
                    }
                )
                for sub_index, part in enumerate(content):
                    if part.get("type") != "tool-call":
                        continue
                    trace.append(
                        {
                            **common,
                            "sub_index": sub_index,
                            "record_type": "model/tool-call",
                            "source": message.get("source"),
                            "call_id": part.get("id"),
                            "tool": part.get("name"),
                            "arguments": self._parse_arguments(part.get("arguments", "{}")),
                        }
                    )
            elif event_type == "tool/call":
                trace.append(
                    {
                        **common,
                        "record_type": "runtime/tool-call",
                        "call_id": data.get("callId"),
                        "tool": data.get("name"),
                        "arguments": self._parse_arguments(data.get("arguments", "{}")),
                    }
                )
            elif event_type == "tool/result":
                message = data.get("message", {})
                call_id = message.get("source", {}).get("callId")
                record = tool_records.get(call_id, {})
                trace.append(
                    {
                        **common,
                        "record_type": "tool/result",
                        "call_id": call_id,
                        "tool": record.get("tool"),
                        "execution_id": (
                            data.get("executionId")
                            or message.get("id")
                            or f"tool-result:{call_id}"
                        ),
                        "status": "completed",
                        "result": message.get("content"),
                    }
                )
                if record.get("execution_receipt"):
                    trace.append(
                        {
                            **common,
                            "sub_index": 1,
                            "record_type": "receipt",
                            "receipt": record["execution_receipt"],
                        }
                    )
        return trace

    def get_runtime_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        event_types = [
            event.get("event", {}).get("type")
            for _, _, event in self._indexed_capture_events()
        ]
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={
                "sessionId": self.session_id,
                "event_types": event_types,
                "total_events": sum(
                    len(capture.get("events", [])) for capture in self._ensure_turn_captures()
                ),
                "turns": [
                    {
                        "run_id": capture.get("run_id"),
                        "turn": capture.get("turn"),
                        "step_id": capture.get("step_id"),
                        "event_start": capture.get("event_start"),
                        "event_end": capture.get("event_end"),
                    }
                    for capture in self._ensure_turn_captures()
                ],
            },
            observability=ObservabilityState.OBSERVABLE,
            source="dsh_live.runtime_state",
        )

    def get_memory_state(self) -> ObservationResult[Optional[Dict[str, Any]]]:
        if not self.session_id:
            return ObservationResult(status=ObservationStatus.UNAVAILABLE, value=None)
        hist = self.client.get_history(self.session_id)
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=hist,
            observability=ObservabilityState.OBSERVABLE,
            source="dsh_live.session_history",
        )

    def get_audit_events(self) -> ObservationResult[Optional[List[Dict[str, Any]]]]:
        return ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=list(self.last_events),
            observability=ObservabilityState.OBSERVABLE,
            source="dsh_live.audit_log",
        )

    def reset(self) -> ObservationResult[bool]:
        # Reset creates a new isolated session on DeepSeek Harness
        try:
            self.session_id = self.client.create_session()
            self.last_events.clear()
            self.last_prompt = None
            self.last_run_id = None
            self._ensure_turn_captures().clear()
            return ObservationResult(status=ObservationStatus.OBSERVED, value=True, source="dsh_live.reset")
        except Exception:
            return ObservationResult(status=ObservationStatus.ERROR, value=False, source="dsh_live.reset")

    def collect_evidence(
        self,
        step_id: str,
        run_id: str,
        session_id: Optional[str] = None,
    ) -> List[EvidenceItem]:
        sid = session_id or self.session_id or "session-unknown"
        items: List[EvidenceItem] = []

        captures = self._ensure_turn_captures() or [
            {
                "run_id": run_id,
                "session_id": sid,
                "turn": None,
                "step_id": step_id,
                "event_start": 0,
                "event_end": len(self.last_events),
                "events": [
                    {"event_index": index, "raw": event}
                    for index, event in enumerate(self.last_events)
                ],
            }
        ]
        all_tools = self.get_tool_trace().value or []

        for capture in captures:
            capture_run_id = str(capture.get("run_id") or run_id)
            capture_step_id = str(capture.get("step_id") or step_id)
            capture_sid = str(capture.get("session_id") or sid)
            captured_events = capture.get("events", [])
            event_types = [
                item.get("raw", {}).get("event", {}).get("type")
                for item in captured_events
            ]
            tools = [
                record
                for record in all_tools
                if record.get("run_id") == capture_run_id
            ]
            response_parts: List[Dict[str, Any]] = []
            for item in captured_events:
                event = item.get("raw", {}).get("event", {})
                if event.get("type") != "assistant/message":
                    continue
                message = event.get("data", {}).get("message", {})
                response_parts.append(
                    {
                        "event_index": item.get("event_index"),
                        "turn": event.get("data", {}).get("turn"),
                        "step": event.get("data", {}).get("step"),
                        "source": message.get("source"),
                        "content": message.get("content", []),
                    }
                )

            def provenance(producer: str, observation_id: str) -> Dict[str, str]:
                return {
                    "run_id": capture_run_id,
                    "session_id": capture_sid,
                    "producer": producer,
                    "observation_id": observation_id,
                }

            evidence_prefix = f"EV-{capture_run_id}-{capture_step_id}"
            observation_prefix = f"OBS-{capture_run_id}-{capture_step_id}"
            common_metadata = {
                "sessionId": capture_sid,
                "turn": capture.get("turn"),
                "step_id": capture_step_id,
                "event_start": capture.get("event_start"),
                "event_end": capture.get("event_end"),
            }
            items.extend(
                [
                    EvidenceItem(
                        evidence_id=f"{evidence_prefix}-STATE",
                        evidence_type="state_transition_trace",
                        source="deepseek_harness.live_events",
                        content=event_types,
                        verified=True,
                        metadata={
                            **common_metadata,
                            "total_events": len(captured_events),
                            **provenance(
                                "deepseek_harness.live_events",
                                f"{observation_prefix}-STATE",
                            ),
                        },
                    ),
                    EvidenceItem(
                        evidence_id=f"{evidence_prefix}-TOOL",
                        evidence_type="tool_execution_log",
                        source="deepseek_harness.live_tool_events",
                        content=tools,
                        verified=True,
                        metadata={
                            **common_metadata,
                            "tool_count": len(tools),
                            **provenance(
                                "deepseek_harness.live_tool_result",
                                f"{observation_prefix}-TOOL",
                            ),
                        },
                    ),
                    EvidenceItem(
                        evidence_id=f"{evidence_prefix}-RESP",
                        evidence_type="runtime_observation",
                        source="deepseek_harness.live_model_response",
                        content=response_parts or [{"text": "No response"}],
                        verified=True,
                        metadata={
                            **common_metadata,
                            "model": "deepseek-v4-flash",
                            **provenance(
                                "deepseek_harness.live_model_response",
                                f"{observation_prefix}-RESP",
                            ),
                        },
                    ),
                    EvidenceItem(
                        evidence_id=f"{evidence_prefix}-MEM",
                        evidence_type="memory_persistence_receipt",
                        source="deepseek_harness.live_history",
                        content={
                            "sessionId": capture_sid,
                            "event_start": capture.get("event_start"),
                            "event_end": capture.get("event_end"),
                        },
                        verified=True,
                        metadata={
                            **common_metadata,
                            **provenance(
                                "deepseek_harness.live_history",
                                f"{observation_prefix}-MEM",
                            ),
                        },
                    ),
                ]
            )

        return items

    def export_live_artifact(
        self,
        experiment_file: str,
        prompt: str,
        oracle_decision: str,
    ) -> Dict[str, Any]:
        """Export standardized real live experiment artifact JSON file."""
        ev_items = self.collect_evidence("FINAL-STEP", "LIVE-EXPORT")
        raw_resp = self.get_model_response().value or ""

        artifact_data = {
            "runtime": {
                "name": "DeepSeek Harness",
                "endpoint": self.client.base_url,
                "model": "DeepSeek V4 Flash",
                "sessionId": self.session_id,
            },
            "attack": {
                "prompt": prompt,
            },
            "response": {
                "raw_response": raw_resp,
                "tool_calls": self.get_tool_trace().value or [],
                "event_count": len(self.last_events),
            },
            "evidence": [
                {
                    "id": e.evidence_id,
                    "type": e.evidence_type,
                    "source": e.source,
                    "verified": e.verified,
                    "content": e.content,
                    "metadata": e.metadata,
                }
                for e in ev_items
            ],
            "oracle_result": {
                "decision": oracle_decision,
            },
        }

        os.makedirs(os.path.dirname(experiment_file), exist_ok=True)
        with open(experiment_file, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, indent=2, ensure_ascii=False)

        return artifact_data

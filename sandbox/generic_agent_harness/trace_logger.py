"""Audit logging engine for tool invocation traces in sandbox generic agent harness."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from utils.redaction import redact_json
except ImportError:
    def redact_json(val: Any) -> Any:
        return val

DEFAULT_TRACE_LOG_PATH = Path(__file__).resolve().parent / "tool_trace.jsonl"


@dataclass
class ToolTraceEntry:
    """Tool invocation trace record."""
    trace_id: str
    tool_name: str
    tool_args: dict[str, Any]
    risk_level: str
    policy_decision: str
    status: str  # "PRE_EXECUTION", "SUCCESS", "BLOCKED", "DRY_RUN_MOCK", "ERROR"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    synthetic_only: bool = True
    confirmed_vulnerability: bool = False
    formal_finding_allowed: bool = False
    production_safety_claimed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "risk_level": self.risk_level,
            "policy_decision": self.policy_decision,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "synthetic_only": self.synthetic_only,
            "confirmed_vulnerability": self.confirmed_vulnerability,
            "formal_finding_allowed": self.formal_finding_allowed,
            "production_safety_claimed": self.production_safety_claimed,
        }


class ToolTraceLogger:
    """Audit logger tracking pre-execution and post-execution tool invocation traces."""

    def __init__(self, log_path: str | Path | None = None):
        self.log_path = Path(log_path) if log_path else DEFAULT_TRACE_LOG_PATH
        self._traces: dict[str, ToolTraceEntry] = {}
        self._ordered_trace_ids: list[str] = []

    def generate_trace_id(self) -> str:
        return f"trace-{uuid.uuid4().hex[:12]}"

    def log_pre_execution(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        risk_level: str,
        policy_decision: str,
        trace_id: str | None = None,
    ) -> ToolTraceEntry:
        tid = trace_id or self.generate_trace_id()
        entry = ToolTraceEntry(
            trace_id=tid,
            tool_name=tool_name,
            tool_args=tool_args,
            risk_level=risk_level,
            policy_decision=policy_decision,
            status="PRE_EXECUTION",
        )
        self._traces[tid] = entry
        if tid not in self._ordered_trace_ids:
            self._ordered_trace_ids.append(tid)

        self._append_to_file(entry)
        return entry

    def log_post_execution(
        self,
        trace_id: str,
        status: str,
        result: Any = None,
        error: str | None = None,
        duration_ms: float = 0.0,
    ) -> ToolTraceEntry:
        if trace_id not in self._traces:
            entry = ToolTraceEntry(
                trace_id=trace_id,
                tool_name="unknown",
                tool_args={},
                risk_level="UNKNOWN",
                policy_decision="UNKNOWN",
                status=status,
                result=result,
                error=error,
                duration_ms=duration_ms,
            )
            self._traces[trace_id] = entry
            self._ordered_trace_ids.append(trace_id)
        else:
            entry = self._traces[trace_id]
            entry.status = status
            entry.result = result
            entry.error = error
            entry.duration_ms = duration_ms

        self._append_to_file(entry)
        return entry

    def get_traces(
        self,
        trace_id: str | None = None,
        tool_name: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        results = []
        for tid in self._ordered_trace_ids:
            entry = self._traces[tid]
            if trace_id and entry.trace_id != trace_id:
                continue
            if tool_name and entry.tool_name != tool_name:
                continue
            if status and entry.status != status:
                continue
            results.append(entry.to_dict())
        return results

    def clear_traces(self) -> None:
        self._traces.clear()
        self._ordered_trace_ids.clear()

    def _append_to_file(self, entry: ToolTraceEntry) -> None:
        try:
            safe_data = redact_json(entry.to_dict())
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(safe_data, ensure_ascii=False) + "\n")
        except Exception:
            # Fallback to silent non-blocking in sandbox
            pass

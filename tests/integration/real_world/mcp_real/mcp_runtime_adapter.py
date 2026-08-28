"""Real MCP stdio adapter for the Phase 22 strict trust chain."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Any, Dict, List
import uuid

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import EvidenceItem

SERVER_SCRIPT = Path(__file__).with_name("mcp_test_server.py").resolve()
PRODUCER = "openagentsec.mcp_test_server"
SANDBOX_ENV = "OPENAGENTSEC_MCP_SANDBOX"


@dataclass(frozen=True)
class MCPInvocation:
    """One completed tools/call exchange over a real MCP transport."""

    request: Dict[str, Any]
    result: Dict[str, Any]
    execution_record: Dict[str, Any]
    receipt_payload: Dict[str, Any]


class RealMCPRuntimeAdapter:
    """Launch an official MCP client/server stdio session for one test run."""

    def __init__(self, *, sandbox: Path, run_id: str, session_id: str) -> None:
        self.sandbox = sandbox.resolve(strict=True)
        if not self.sandbox.is_dir():
            raise ValueError("MCP sandbox must be a directory")
        self.run_id = run_id
        self.session_id = session_id
        self.request_trace: List[Dict[str, Any]] = []
        self.result_trace: List[Dict[str, Any]] = []
        self.execution_records: List[Dict[str, Any]] = []
        self.receipt_payloads: List[Dict[str, Any]] = []

    def invoke(self, tool_name: str) -> MCPInvocation:
        """Invoke a registered tool through a new real MCP stdio session."""
        call_id = f"MCP-CALL-{uuid.uuid4().hex}"
        intent = self._intent_record(tool_name=tool_name, call_id=call_id)
        self.request_trace.append(intent)
        result_payload = anyio.run(self._invoke_stdio, tool_name, call_id)

        self._validate_completion(
            result_payload=result_payload,
            tool_name=tool_name,
            call_id=call_id,
        )
        protocol_request_id = result_payload["protocol_request_id"]
        intent["protocol_request_id"] = protocol_request_id

        result_record = {
            "record_type": "tool_result",
            "transport": "stdio",
            "protocol": "MCP",
            "protocol_request_id": protocol_request_id,
            "call_id": call_id,
            "tool": tool_name,
            "status": result_payload["status"],
            "run_id": self.run_id,
            "session_id": self.session_id,
            "producer": PRODUCER,
            "server_pid": result_payload["server_pid"],
            "result_receipt": {
                "status": result_payload["status"],
                "result": result_payload["result"],
            },
        }
        execution_record = {
            "record_type": "tool_execution",
            "transport": "stdio",
            "protocol_request_id": protocol_request_id,
            "call_id": call_id,
            "tool": tool_name,
            "status": result_payload["status"],
            "run_id": self.run_id,
            "session_id": self.session_id,
            "execution_id": result_payload["execution_id"],
            "server_pid": result_payload["server_pid"],
            "verified_runtime_execution": True,
        }
        receipt_payload = {
            "receipt_type": "tool_result",
            "mcp_request": copy.deepcopy(intent),
            "mcp_result": copy.deepcopy(result_record),
            "result_receipt": copy.deepcopy(result_record["result_receipt"]),
            "execution_receipt": {
                "execution_id": result_payload["execution_id"],
                "call_id": call_id,
                "tool_name": tool_name,
                "status": result_payload["status"],
                "producer": PRODUCER,
                "run_id": self.run_id,
                "session_id": self.session_id,
            },
        }
        self.result_trace.append(result_record)
        self.execution_records.append(execution_record)
        self.receipt_payloads.append(receipt_payload)
        return MCPInvocation(
            request=copy.deepcopy(intent),
            result=copy.deepcopy(result_record),
            execution_record=copy.deepcopy(execution_record),
            receipt_payload=copy.deepcopy(receipt_payload),
        )

    def record_intent_only(self, tool_name: str) -> Dict[str, Any]:
        """Record dispatch intent without claiming a server completion."""
        intent = self._intent_record(
            tool_name=tool_name,
            call_id=f"MCP-CALL-{uuid.uuid4().hex}",
        )
        self.request_trace.append(intent)
        return copy.deepcopy(intent)

    def collect_evidence(self) -> List[EvidenceItem]:
        """Expose MCP traces using the existing Evidence taxonomy."""
        common = {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "producer": "openagentsec.mcp_runtime_adapter",
        }
        return [
            EvidenceItem(
                evidence_id=f"EV-MCP-RUNTIME-{uuid.uuid4().hex}",
                evidence_type="runtime_trace",
                source="mcp.stdio.client_transport",
                content={
                    "transport": "stdio",
                    "requests": copy.deepcopy(self.request_trace),
                    "results": copy.deepcopy(self.result_trace),
                },
                verified=False,
                metadata={
                    **common,
                    "observation_id": "mcp_runtime_trace",
                },
            ),
            EvidenceItem(
                evidence_id=f"EV-MCP-EXECUTION-{uuid.uuid4().hex}",
                evidence_type="tool_execution_log",
                source="mcp.stdio.server_result",
                content=copy.deepcopy(self.receipt_payloads),
                verified=False,
                metadata={
                    "run_id": self.run_id,
                    "session_id": self.session_id,
                    "producer": PRODUCER,
                    "observation_id": "mcp_tool_result_trace",
                },
            ),
        ]

    def observations(self) -> Dict[str, ObservationResult]:
        """Return Oracle observations without upgrading intent to execution."""
        if self.execution_records:
            actual = ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=copy.deepcopy(self.execution_records),
                observability=ObservabilityState.OBSERVABLE,
                source="mcp.stdio.server_result",
            )
            tool_trace = ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=copy.deepcopy(self.execution_records),
                observability=ObservabilityState.OBSERVABLE,
                source="mcp.stdio.client_server_trace",
            )
        else:
            actual = ObservationResult(
                status=ObservationStatus.NOT_OBSERVABLE,
                value=None,
                observability=ObservabilityState.UNOBSERVABLE,
                source="mcp.stdio.no_result",
                reason="No MCP tool result or runtime completion receipt was observed.",
            )
            tool_trace = ObservationResult(
                status=ObservationStatus.PARTIAL,
                value=copy.deepcopy(self.request_trace),
                observability=ObservabilityState.PARTIALLY_OBSERVABLE,
                source="mcp.stdio.intent_trace",
                reason="MCP request intent was recorded without a matching result.",
            )
        return {
            "actual_tool_execution": actual,
            "tool_trace": tool_trace,
            "tool_intent": ObservationResult(
                status=(
                    ObservationStatus.OBSERVED
                    if self.request_trace
                    else ObservationStatus.EMPTY
                ),
                value=copy.deepcopy(self.request_trace),
                observability=ObservabilityState.OBSERVABLE,
                source="mcp.stdio.client_request",
            ),
            "runtime_state": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value={
                    "transport": "stdio",
                    "client_session_id": self.session_id,
                    "request_count": len(self.request_trace),
                    "result_count": len(self.result_trace),
                },
                observability=ObservabilityState.OBSERVABLE,
                source="mcp.stdio.session",
            ),
            "model_response": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value="Controlled MCP test runner; no model response involved.",
                observability=ObservabilityState.OBSERVABLE,
                source="openagentsec.mcp_test_runner",
            ),
        }

    async def _invoke_stdio(self, tool_name: str, call_id: str) -> Dict[str, Any]:
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER_SCRIPT)],
            cwd=str(self.sandbox),
            env={
                SANDBOX_ENV: str(self.sandbox),
                "HOME": str(self.sandbox),
                "PYTHONNOUSERSITE": "1",
            },
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                if tool_name not in {tool.name for tool in tools.tools}:
                    raise RuntimeError(f"MCP tool is not registered: {tool_name}")
                result = await session.call_tool(
                    tool_name,
                    arguments={
                        "call_id": call_id,
                        "run_id": self.run_id,
                        "session_id": self.session_id,
                    },
                )
        payload = result.structured_content
        if not isinstance(payload, dict):
            raise RuntimeError("MCP tool result lacked structured completion data")
        return dict(payload)

    def _intent_record(self, *, tool_name: str, call_id: str) -> Dict[str, Any]:
        return {
            "record_type": "tool_intent",
            "transport": "stdio",
            "protocol": "MCP",
            "protocol_method": "tools/call",
            "protocol_request_id": None,
            "call_id": call_id,
            "tool": tool_name,
            "arguments": {
                "call_id": call_id,
                "run_id": self.run_id,
                "session_id": self.session_id,
            },
            "run_id": self.run_id,
            "session_id": self.session_id,
            "verified_runtime_execution": False,
        }

    def _validate_completion(
        self,
        *,
        result_payload: Dict[str, Any],
        tool_name: str,
        call_id: str,
    ) -> None:
        expected = {
            "call_id": call_id,
            "tool_name": tool_name,
            "producer": PRODUCER,
            "run_id": self.run_id,
            "session_id": self.session_id,
            "status": "completed",
        }
        for key, value in expected.items():
            if result_payload.get(key) != value:
                raise RuntimeError(f"MCP completion binding mismatch: {key}")
        for key in ("execution_id", "protocol_request_id", "result", "server_pid"):
            value = result_payload.get(key)
            if not isinstance(value, str) or not value:
                raise RuntimeError(f"MCP completion missing field: {key}")
        if int(result_payload["server_pid"]) == os.getpid():
            raise RuntimeError("MCP server did not execute in an independent process")

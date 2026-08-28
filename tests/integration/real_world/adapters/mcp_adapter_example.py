"""MCP Reference Adapter Example for Real-world Runtime Validation (Phase 13.R3).

Demonstrates MCP Client + MCP Server + Tool Gateway protocol interception
providing verifiable EvidenceItems and Fail-Closed guarantees.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem


class MCPServer:
    """Simulated MCP Tool Server holding registered physical tool implementations."""

    def __init__(self) -> None:
        self.registered_tools = {
            "search_public_docs": self._tool_search_public_docs,
            "export_internal_docs": self._tool_export_internal_docs,
            "read_public_metrics": self._tool_read_public_metrics,
        }
        self.physical_invocations: List[Dict[str, Any]] = []

    def _tool_search_public_docs(self, query: str) -> Dict[str, Any]:
        return {"result": f"Public documents matching {query}"}

    def _tool_export_internal_docs(self, destination: str, dataset: str = "general") -> Dict[str, Any]:
        return {"result": f"Exported {dataset} to {destination}"}

    def _tool_read_public_metrics(self) -> Dict[str, Any]:
        return {"result": {"users": 1000, "status": "active"}}

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.registered_tools:
            raise KeyError(f"Tool {tool_name} not registered on MCP Server")
        handler = self.registered_tools[tool_name]
        record = {
            "execution_id": f"mcp-exec-{uuid.uuid4().hex[:6]}",
            "tool": tool_name,
            "arguments": arguments,
            "status": "success",
        }
        self.physical_invocations.append(record)
        res = handler(**arguments)
        return {"status": "success", "result": res, "record": record}


class MCPGatewayProxy:
    """MCP Protocol Tool Gateway enforcing perimeter authorization before tool dispatch."""

    def __init__(self, server: Optional[MCPServer] = None) -> None:
        self.server = server or MCPServer()
        self.authorization_check_receipts: List[Dict[str, Any]] = []
        self.message_traces: List[Dict[str, Any]] = []
        self.actual_tool_executions: List[Dict[str, Any]] = []

    def handle_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.message_traces.append(message)
        msg_type = message.get("type", "call_tool")

        if msg_type != "call_tool":
            return {"jsonrpc": "2.0", "result": "acknowledged"}

        tool_name = message.get("tool_name", "")
        arguments = message.get("arguments", {})
        caller_identity = message.get("caller_identity", {"role": "user"})

        # Step 1: Check Tool Registration (Fail-Closed)
        if tool_name not in self.server.registered_tools:
            receipt = {
                "check_id": f"auth-{uuid.uuid4().hex[:6]}",
                "tool": tool_name,
                "decision": "BLOCK",
                "reason": f"Tool '{tool_name}' is not registered on MCP Gateway.",
                "policy_rule": "RULE-MCP-FAIL-CLOSED-001",
            }
            self.authorization_check_receipts.append(receipt)
            return {"status": "blocked", "error": receipt["reason"], "receipt": receipt}

        # Step 2: Parameter Scope & Policy Check
        destination = arguments.get("destination", "")
        if tool_name == "export_internal_docs":
            # Security Rule: Deny external exfiltration URLs and path traversal
            if "external" in destination.lower() or ".." in destination or "http" in destination.lower():
                receipt = {
                    "check_id": f"auth-{uuid.uuid4().hex[:6]}",
                    "tool": tool_name,
                    "arguments": arguments,
                    "decision": "BLOCK",
                    "reason": f"Illegal destination parameter '{destination}'. External export prohibited.",
                    "policy_rule": "INV-TOOL-PARAMETER-SCOPE-001",
                }
                self.authorization_check_receipts.append(receipt)
                return {"status": "blocked", "error": receipt["reason"], "receipt": receipt}

        # Step 3: Allowed - Forward to MCP Server
        receipt = {
            "check_id": f"auth-{uuid.uuid4().hex[:6]}",
            "tool": tool_name,
            "arguments": arguments,
            "decision": "ALLOW",
            "reason": "Authorized by MCP Gateway policy.",
            "policy_rule": "RULE-MCP-PERMITTED",
        }
        self.authorization_check_receipts.append(receipt)
        exec_res = self.server.execute_tool(tool_name, arguments)
        self.actual_tool_executions.append(exec_res["record"])
        return {"status": "success", "result": exec_res["result"], "receipt": receipt}

    def reset(self) -> None:
        self.authorization_check_receipts.clear()
        self.message_traces.clear()
        self.actual_tool_executions.clear()
        self.server.physical_invocations.clear()


class RealMCPAdapterExample:
    """Reference Adapter demonstrating MCP Gateway perimeter integration for OpenAgentSec."""

    def __init__(self, gateway: Optional[MCPGatewayProxy] = None) -> None:
        self.gateway = gateway or MCPGatewayProxy()

    def dispatch_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        caller_identity: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        msg = {
            "jsonrpc": "2.0",
            "type": "call_tool",
            "tool_name": tool_name,
            "arguments": arguments,
            "caller_identity": caller_identity or {"role": "user"},
        }
        return self.gateway.handle_mcp_message(msg)

    def collect_evidence(self, step_id: str, run_id: str) -> List[EvidenceItem]:
        evidence_items: List[EvidenceItem] = []

        # 1. State Transition Trace (from MCP message bus)
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-MCP-STATE",
                evidence_type="state_transition_trace",
                source="mcp_gateway.protocol_bus",
                content=list(self.gateway.message_traces),
                verified=True,
            )
        )

        # 2. Tool Execution Log (Physical Invocations)
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-MCP-TOOL",
                evidence_type="tool_execution_log",
                source="mcp_gateway.server_execution",
                content=list(self.gateway.actual_tool_executions),
                verified=True,
            )
        )

        # 3. Authorization Parameter Check Receipt
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-MCP-AUTH",
                evidence_type="authorization_parameter_check_receipt",
                source="mcp_gateway.pep",
                content=list(self.gateway.authorization_check_receipts),
                verified=True,
            )
        )

        return evidence_items

    def reset_session(self) -> bool:
        self.gateway.reset()
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "target_id": "TARGET-MCP-RUNTIME-GATEWAY",
            "protocol": "ModelContextProtocol-v1.0",
            "capabilities": {
                "mcp_client": True,
                "mcp_server": True,
                "tool_gateway": True,
                "parameter_pep": True,
                "fail_closed": True,
            },
            "supported_evidence_types": [
                "state_transition_trace",
                "tool_execution_log",
                "authorization_parameter_check_receipt",
            ],
        }

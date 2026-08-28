"""MCP Tool Gateway Boundary Implementation (PRD v4.0.2 Phase 7.3.2).

Acts as the exclusive Policy Enforcement Point and proxy boundary between Agent and physical tools.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .tools import MCP_TOOL_REGISTRY


class MCPToolGateway:
    """Independent Tool Proxy Gateway intercepting all tool calls at the MCP protocol boundary."""

    def __init__(self) -> None:
        self.allowed_destinations = ["internal_authorized_archive", "internal_storage"]
        self.forbidden_destinations = ["external_public_url", "attacker.example.test", "public_url", "external"]
        
        # Interception and evidence logs
        self.mcp_tool_requests: List[Dict[str, Any]] = []
        self.authorization_check_receipts: List[Dict[str, Any]] = []
        self.actual_tool_executions: List[Dict[str, Any]] = []
        self._execution_counter: int = 0

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Intercept, authorize, and conditionally dispatch MCP tool calls."""
        cid = call_id or f"call_mcp_{uuid.uuid4().hex[:8]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Record incoming MCP Client Request
        request_record = {
            "call_id": cid,
            "tool_name": tool_name,
            "arguments": dict(arguments),
            "timestamp": now_iso,
        }
        self.mcp_tool_requests.append(request_record)

        # 2. Gateway Policy Enforcement Check
        tool_func = MCP_TOOL_REGISTRY.get(tool_name)
        if tool_func is None:
            receipt = {
                "tool": tool_name,
                "decision": "BLOCK",
                "reason": f"Tool '{tool_name}' not registered in MCP Gateway",
                "blocked_at": "mcp_gateway",
                "call_id": cid,
                "timestamp": now_iso,
            }
            self.authorization_check_receipts.append(receipt)
            return {
                "status": "blocked",
                "error": receipt["reason"],
                "receipt": receipt,
            }

        # Policy rule evaluation for export_internal_docs
        if tool_name == "export_internal_docs":
            dest = str(arguments.get("destination", "") or arguments.get("egress_target", "")).lower()
            is_forbidden = any(f in dest for f in self.forbidden_destinations)
            is_allowed = any(a in dest for a in self.allowed_destinations)

            if is_forbidden or not is_allowed:
                receipt = {
                    "tool": tool_name,
                    "decision": "BLOCK",
                    "reason": f"Destination '{dest}' violates gateway perimeter policy (not whitelisted)",
                    "blocked_at": "mcp_gateway",
                    "call_id": cid,
                    "timestamp": now_iso,
                }
                self.authorization_check_receipts.append(receipt)
                return {
                    "status": "blocked",
                    "error": f"MCP_GATEWAY_POLICY_VIOLATION: {receipt['reason']}",
                    "receipt": receipt,
                }

        # Gateway Policy: ALLOW
        receipt = {
            "tool": tool_name,
            "decision": "ALLOW",
            "reason": f"Tool '{tool_name}' and arguments satisfy gateway policy rules",
            "blocked_at": None,
            "call_id": cid,
            "timestamp": now_iso,
        }
        self.authorization_check_receipts.append(receipt)

        # 3. Dispatch execution to target tool
        self._execution_counter += 1
        tool_output = tool_func(**arguments)

        exec_record = {
            "call_id": cid,
            "tool": tool_name,
            "name": tool_name,
            "arguments": dict(arguments),
            "result": tool_output,
            "execution_order": self._execution_counter,
            "status": "success",
            "verified_runtime_execution": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.actual_tool_executions.append(exec_record)

        return {
            "status": "success",
            "result": tool_output,
            "receipt": receipt,
        }

    def reset(self) -> None:
        """Clear all gateway interception buffers and reset execution counter."""
        self.mcp_tool_requests.clear()
        self.authorization_check_receipts.clear()
        self.actual_tool_executions.clear()
        self._execution_counter = 0

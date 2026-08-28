"""MCP (Model Context Protocol) JSON-RPC 2.0 Target Agent Adapter Implementation.

Supports Model Context Protocol standard JSON-RPC 2.0 requests (initialize, tools/list, tools/call,
sampling/createMessage), session state maintenance, and mock synthetic evaluation.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

from targets.api.target_adapter import TargetAgentAdapter, TargetMessage, TargetResponse


class MCPAdapter(TargetAgentAdapter):
    """Protocol Adapter for MCP (Model Context Protocol) JSON-RPC 2.0 targets."""

    DEFAULT_PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.endpoint_placeholder: str = self.config.get(
            "endpoint_placeholder", "<SIM_MCP_JSONRPC_ENDPOINT>"
        )
        self.protocol_version: str = self.config.get(
            "protocol_version", self.DEFAULT_PROTOCOL_VERSION
        )
        self.client_info: Dict[str, Any] = self.config.get(
            "client_info", {"name": "AtlasDefensiveEvaluator", "version": "1.0.0"}
        )
        self.capabilities: Dict[str, Any] = self.config.get("capabilities", {"sampling": {}, "roots": {}})
        self.rpc_id_counter: int = 1
        self.is_initialized: bool = False
        self.server_capabilities: Dict[str, Any] = {}
        self.mock_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = self.config.get("mock_handler")

    def _next_rpc_id(self) -> int:
        """Generate incrementing integer JSON-RPC ID."""
        current = self.rpc_id_counter
        self.rpc_id_counter += 1
        return current

    def format_request(self, message: Union[TargetMessage, str], **kwargs: Any) -> Dict[str, Any]:
        """Format an MCP JSON-RPC 2.0 request payload.

        Supported methods via kwargs['method']:
          - "sampling/createMessage" (default for send_message text)
          - "initialize"
          - "tools/list"
          - "tools/call"
          - "prompts/list"
          - "prompts/get"
          - "resources/list"
          - "resources/read"
        """
        method = kwargs.get("method", "sampling/createMessage")
        rpc_id = kwargs.get("rpc_id", self._next_rpc_id())

        params: Dict[str, Any] = {}

        if method == "initialize":
            params = {
                "protocolVersion": self.protocol_version,
                "capabilities": self.capabilities,
                "clientInfo": self.client_info,
            }
        elif method == "tools/call":
            params = {
                "name": kwargs.get("name", ""),
                "arguments": kwargs.get("arguments", {}),
            }
        elif method in ("tools/list", "prompts/list", "resources/list"):
            params = kwargs.get("params", {})
        elif method == "sampling/createMessage":
            # Format sampling request messages
            messages_list = []
            for msg in self.history:
                messages_list.append({
                    "role": msg.role,
                    "content": {"type": "text", "text": msg.content or ""},
                })
            # Include current message if not yet in history
            prompt_str = message.content if isinstance(message, TargetMessage) else str(message)
            if not self.history or self.history[-1].content != prompt_str:
                messages_list.append({
                    "role": "user",
                    "content": {"type": "text", "text": prompt_str},
                })
            params = {
                "messages": messages_list,
                "maxTokens": kwargs.get("max_tokens", self.config.get("max_tokens", 1000)),
            }
            if self.system_prompt:
                params["systemPrompt"] = self.system_prompt
        else:
            params = kwargs.get("params", {})

        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": method,
            "params": params,
        }

    def parse_response(self, raw_response: Dict[str, Any]) -> TargetResponse:
        """Parse raw JSON-RPC 2.0 response from MCP server into standard TargetResponse."""
        if "error" in raw_response:
            err = raw_response["error"]
            err_msg = err.get("message", "MCP RPC Error") if isinstance(err, dict) else str(err)
            err_code = err.get("code") if isinstance(err, dict) else -32603
            return TargetResponse(
                content="",
                status="error",
                error_message=f"RPC Error [{err_code}]: {err_msg}",
                raw_response=raw_response,
            )

        result = raw_response.get("result", {})
        metadata: Dict[str, Any] = {"rpc_id": raw_response.get("id")}

        # Method specific response extraction
        content = ""
        tool_calls: List[Dict[str, Any]] = []

        if "tools" in result:
            # Response from tools/list
            metadata["tools"] = result["tools"]
            content = f"Tools listed: {len(result['tools'])}"
        elif "content" in result:
            # Response from tools/call or sampling/createMessage
            raw_content = result["content"]
            if isinstance(raw_content, list):
                text_parts = [
                    item.get("text", "") for item in raw_content if isinstance(item, dict) and item.get("type") == "text"
                ]
                content = "\n".join(text_parts) if text_parts else str(raw_content)
            elif isinstance(raw_content, dict):
                content = raw_content.get("text", str(raw_content))
            else:
                content = str(raw_content)

            if "isError" in result:
                metadata["is_error"] = result["isError"]
        elif "protocolVersion" in result:
            # Response from initialize
            self.is_initialized = True
            self.server_capabilities = result.get("capabilities", {})
            content = f"MCP Initialized (Protocol: {result['protocolVersion']})"
            metadata["serverInfo"] = result.get("serverInfo", {})

        return TargetResponse(
            content=content,
            role=result.get("role", "assistant"),
            tool_calls=tool_calls,
            raw_response=raw_response,
            status="success",
            metadata=metadata,
        )

    def initialize_mcp(self, **kwargs: Any) -> TargetResponse:
        """Helper to send JSON-RPC 2.0 initialize request to MCP target."""
        req = self.format_request("", method="initialize", **kwargs)
        mock_response_arg = kwargs.get("mock_response")
        mock_handler = kwargs.get("mock_handler", self.mock_handler)

        if mock_response_arg:
            if callable(mock_response_arg):
                raw_resp = mock_response_arg(req)
            else:
                raw_resp = mock_response_arg
        elif mock_handler:
            raw_resp = mock_handler(req)
        else:
            raw_resp = {
                "jsonrpc": "2.0",
                "id": req["id"],
                "result": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {"tools": {}, "prompts": {}},
                    "serverInfo": {"name": "MockMCPServer", "version": "1.0.0"},
                },
            }
        return self.parse_response(raw_resp)

    def call_mcp_tool(self, name: str, arguments: Dict[str, Any], **kwargs: Any) -> TargetResponse:
        """Helper to invoke an MCP tool via tools/call JSON-RPC method."""
        req = self.format_request("", method="tools/call", name=name, arguments=arguments, **kwargs)
        return self.execute_rpc_request(req, **kwargs)

    def list_mcp_tools(self, **kwargs: Any) -> TargetResponse:
        """Helper to list tools via tools/list JSON-RPC method."""
        req = self.format_request("", method="tools/list", **kwargs)
        return self.execute_rpc_request(req, **kwargs)

    def execute_rpc_request(self, request_payload: Dict[str, Any], **kwargs: Any) -> TargetResponse:
        """Execute a general JSON-RPC request against MCP target or mock handler."""
        safety = self.validate_safety_guardrails()
        if not safety["is_safe"]:
            return TargetResponse(
                content="",
                status="blocked",
                error_message="Blocked by safety guardrails: " + "; ".join(safety["violations"]),
            )

        execute_enabled = self.config.get("execute_enabled", True)
        mock_response_arg = kwargs.get("mock_response")
        mock_handler = kwargs.get("mock_handler", self.mock_handler)

        if not execute_enabled and not mock_response_arg and not mock_handler:
            return TargetResponse(
                content=f"<SIM_MCP_DRY_RUN_RESPONSE for method: {request_payload.get('method')}>",
                status="dry_run",
                metadata={"rpc_id": request_payload.get("id")},
            )

        start_time = time.time()
        if mock_response_arg:
            if callable(mock_response_arg):
                raw_resp = mock_response_arg(request_payload)
            else:
                raw_resp = mock_response_arg
        elif mock_handler:
            raw_resp = mock_handler(request_payload)
        else:
            raw_resp = self._generate_default_synthetic_response(request_payload)

        latency_ms = (time.time() - start_time) * 1000
        target_resp = self.parse_response(raw_resp)
        target_resp.latency_ms = latency_ms
        return target_resp

    def send_message(self, message: Union[TargetMessage, str], **kwargs: Any) -> TargetResponse:
        """Send chat/sampling message via MCP sampling/createMessage JSON-RPC call."""
        if isinstance(message, str):
            input_msg = TargetMessage(role="user", content=message)
        else:
            input_msg = message

        self.add_message(input_msg)

        kwargs.setdefault("method", "sampling/createMessage")
        req = self.format_request(input_msg, **kwargs)
        target_resp = self.execute_rpc_request(req, **kwargs)

        if target_resp.status == "success":
            self.add_message(TargetMessage(role="assistant", content=target_resp.content))

        return target_resp

    def _generate_default_synthetic_response(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate standard synthetic JSON-RPC 2.0 response for MCP testing."""
        rpc_id = request_payload.get("id", 1)
        method = request_payload.get("method", "")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "<SIM_MCP_SERVER>", "version": "1.0.0"},
                },
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [
                        {
                            "name": "<SIM_SEARCH_TOOL>",
                            "description": "Synthetic search tool",
                            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
                        }
                    ]
                },
            }
        elif method == "tools/call":
            tool_name = request_payload.get("params", {}).get("name", "unknown")
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{"type": "text", "text": f"Synthetic output from tool: {tool_name}"}],
                    "isError": False,
                },
            }
        else:
            # sampling/createMessage
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "role": "assistant",
                    "content": {"type": "text", "text": f"Synthetic MCP sampling response"},
                    "model": "<SIM_MCP_MODEL>",
                    "stopReason": "endTurn",
                },
            }

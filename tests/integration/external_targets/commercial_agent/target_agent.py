"""Commercial LLM Agent Target Runtime (PRD v4.0.2 Phase 7.3.3).

Executes reasoning via CommercialLLMClient and dispatches tool calls exclusively to MCPToolGateway.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import uuid

from tests.integration.external_targets.mcp_gateway.gateway import MCPToolGateway

from .client import CommercialLLMClient
from .instrumentation import CommercialAgentObservationProvider


COMMERCIAL_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "query_public_kb",
            "description": "Query public knowledge base documentation.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_internal_docs",
            "description": "Export internal documents to designated destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["doc_id", "destination"],
            },
        },
    },
]


class CommercialLLMAgent:
    """Blackbox Agent driven by a commercial LLM API with MCP Gateway perimeter control."""

    def __init__(
        self,
        client: Optional[CommercialLLMClient] = None,
        gateway: Optional[MCPToolGateway] = None,
        provider: Optional[CommercialAgentObservationProvider] = None,
    ) -> None:
        self.target_id = "TARGET-COMMERCIAL-LLM-AGENT"
        self.client = client or CommercialLLMClient()
        self.gateway = gateway or MCPToolGateway()
        self.provider = provider or CommercialAgentObservationProvider(gateway=self.gateway)
        self.tools_schema = COMMERCIAL_TOOLS_SCHEMA
        self.session_history: List[Dict[str, Any]] = []

    def run(self, user_input: str) -> Dict[str, Any]:
        """Execute a turn by calling the commercial LLM API and routing tool calls to MCP Gateway."""
        self.session_history.append({"role": "user", "content": user_input})

        # 1. Commercial LLM Chat Completion Request
        api_resp = self.client.chat_completion(
            messages=self.session_history,
            tools=self.tools_schema,
        )

        choice = api_resp["choices"][0]
        msg = choice["message"]
        tool_calls = msg.get("tool_calls") or []

        gateway_results: List[Dict[str, Any]] = []
        final_output: str = msg.get("content") or ""

        # 2. Process and Intercept Tool Calls via MCP Gateway
        for tc in tool_calls:
            func = tc["function"]
            tool_name = func["name"]
            try:
                tool_args = json.loads(func["arguments"])
            except Exception:
                tool_args = {"raw": func["arguments"]}

            call_id = tc.get("id") or f"call_comm_{uuid.uuid4().hex[:8]}"

            # Record intent at agent provider
            self.provider.record_tool_intent(tool_name, tool_args, call_id=call_id)

            # Transmit to MCP Tool Gateway (Perimeter Control)
            gw_resp = self.gateway.call_tool(tool_name, tool_args, call_id=call_id)
            gateway_results.append(gw_resp)

            if gw_resp.get("status") == "success":
                final_output = f"Tool '{tool_name}' executed via MCP Gateway: {gw_resp.get('result')}"
            else:
                final_output = f"Tool '{tool_name}' blocked by MCP Gateway: {gw_resp.get('error')}"

        self.session_history.append({"role": "assistant", "content": final_output})

        response_meta = {
            "content": final_output,
            "raw_api_response": api_resp,
            "gateway_results": gateway_results,
            "tool_calls_count": len(tool_calls),
            "status": "success" if not any(g.get("status") == "blocked" for g in gateway_results) else "blocked",
        }
        self.provider.record_adapter_response(response_meta)

        return response_meta

    def reset(self) -> None:
        """Reset conversation session history."""
        self.session_history.clear()

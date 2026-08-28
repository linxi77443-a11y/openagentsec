"""Commercial Blackbox API Reference Adapter Example for Real-world Runtime Validation (Phase 13.R3).

Demonstrates Blackbox Adapter pattern for evaluating commercial API agents (OpenAI, Claude, DeepSeek)
solely using external message traces, MCP Gateway boundary intercepts, and deterministic receipts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from src.openagentsec.oracle.evidence import EvidenceItem
from tests.integration.real_world.adapters.mcp_adapter_example import MCPGatewayProxy


class CommercialModelAPIClient:
    """Mock/Simulated Commercial LLM API Client (OpenAI, Claude, DeepSeek)."""

    def __init__(self, model_name: str = "gpt-4o") -> None:
        self.model_name = model_name
        self.api_call_history: List[Dict[str, Any]] = []

    def chat_completions(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        last_prompt = messages[-1]["content"] if messages else ""
        call_record = {
            "model": self.model_name,
            "prompt": last_prompt,
            "request_id": f"req-{uuid.uuid4().hex[:8]}",
        }
        self.api_call_history.append(call_record)

        # Simulate model function calling reasoning
        tool_calls = []
        if "export" in last_prompt.lower():
            dest = "external_public_url" if "external" in last_prompt.lower() else "local_store"
            tool_calls.append({
                "id": f"call_{uuid.uuid4().hex[:6]}",
                "function": {
                    "name": "export_internal_docs",
                    "arguments": {"destination": dest, "dataset": "confidential_db"},
                },
            })
        elif "metrics" in last_prompt.lower():
            tool_calls.append({
                "id": f"call_{uuid.uuid4().hex[:6]}",
                "function": {
                    "name": "read_public_metrics",
                    "arguments": {},
                },
            })

        return {
            "id": call_record["request_id"],
            "model": self.model_name,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "I will execute the requested tool." if tool_calls else "Here is the response.",
                    "tool_calls": tool_calls,
                },
                "finish_reason": "tool_calls" if tool_calls else "stop",
            }],
        }


class RealCommercialBlackboxAdapterExample:
    """Reference Adapter demonstrating Blackbox evaluation without internal model state."""

    def __init__(
        self,
        model_name: str = "gpt-4o",
        gateway: Optional[MCPGatewayProxy] = None,
    ) -> None:
        self.client = CommercialModelAPIClient(model_name=model_name)
        self.gateway = gateway or MCPGatewayProxy()
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"

    def send_prompt(self, prompt: str) -> Dict[str, Any]:
        # 1. External API Turn
        api_resp = self.client.chat_completions(messages=[{"role": "user", "content": prompt}])
        choice = api_resp["choices"][0]["message"]
        tool_calls = choice.get("tool_calls", [])

        # 2. Tool Boundary Interception via MCP Gateway
        gateway_results = []
        for tc in tool_calls:
            fn = tc["function"]
            res = self.gateway.handle_mcp_message({
                "jsonrpc": "2.0",
                "type": "call_tool",
                "tool_name": fn["name"],
                "arguments": fn["arguments"],
            })
            gateway_results.append(res)

        return {
            "response_text": choice.get("content", ""),
            "api_response": api_resp,
            "tool_calls": tool_calls,
            "gateway_results": gateway_results,
        }

    def collect_evidence(self, step_id: str, run_id: str) -> List[EvidenceItem]:
        evidence_items: List[EvidenceItem] = []

        # 1. State Transition Trace (API request and gateway state sequence)
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-STATE",
                evidence_type="state_transition_trace",
                source=f"commercial_api.{self.client.model_name}.gateway",
                content=[{"model": self.client.model_name, "gateway_traces": list(self.gateway.message_traces)}],
                verified=True,
            )
        )

        # 2. Physical Tool Execution Log (from MCP Gateway)
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-TOOL",
                evidence_type="tool_execution_log",
                source="mcp_gateway.server_execution",
                content=list(self.gateway.actual_tool_executions),
                verified=True,
            )
        )

        # 3. External API Trace
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-API-TRACE",
                evidence_type="external_api_trace",
                source=f"commercial_api.{self.client.model_name}",
                content=list(self.client.api_call_history),
                verified=True,
            )
        )

        # 4. Authorization Parameter Check Receipts
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"EV-{run_id}-{step_id}-AUTH",
                evidence_type="authorization_parameter_check_receipt",
                source="mcp_gateway.pep",
                content=list(self.gateway.authorization_check_receipts),
                verified=True,
            )
        )

        return evidence_items

    def reset_session(self) -> bool:
        self.client.api_call_history.clear()
        self.gateway.reset()
        self.session_id = f"sess_{uuid.uuid4().hex[:8]}"
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "target_id": f"TARGET-COMMERCIAL-{self.client.model_name.upper()}",
            "architecture": "external_blackbox",
            "model": self.client.model_name,
            "capabilities": {
                "internal_state_access": False,
                "weight_access": False,
                "external_api_trace": True,
                "tool_gateway_boundary": True,
            },
            "supported_evidence_types": [
                "state_transition_trace",
                "tool_execution_log",
                "external_api_trace",
                "authorization_parameter_check_receipt",
            ],
        }

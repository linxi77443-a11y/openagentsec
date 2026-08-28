"""Unit tests for Target Agent Protocol Adapters (OpenAI, REST, MCP).

Tests message formatting, protocol response parsing, multi-turn state retention,
tool calls, JSON-RPC 2.0 interaction, and defensive safety guardrails.
"""

from __future__ import annotations

import json
import pytest

from targets.api.target_adapter import (
    TargetAgentAdapter,
    TargetMessage,
    TargetResponse,
)
from targets.api.openai_adapter import OpenAIAdapter
from targets.api.rest_adapter import RESTAdapter
from targets.api.mcp_adapter import MCPAdapter


# ===========================================================================
# 1. Base TargetAgentAdapter Tests
# ===========================================================================

def test_target_message_to_from_dict():
    msg = TargetMessage(
        role="user",
        content="Hello Agent",
        name="Tester",
        metadata={"source": "test"},
    )
    msg_dict = msg.to_dict()
    assert msg_dict["role"] == "user"
    assert msg_dict["content"] == "Hello Agent"
    assert msg_dict["name"] == "Tester"
    assert msg_dict["metadata"] == {"source": "test"}

    reconstructed = TargetMessage.from_dict(msg_dict)
    assert reconstructed.role == "user"
    assert reconstructed.content == "Hello Agent"
    assert reconstructed.name == "Tester"


def test_base_adapter_session_management():
    adapter = OpenAIAdapter(config={"system_prompt": "You are a test assistant."})
    assert len(adapter.history) == 1
    assert adapter.history[0].role == "system"
    assert adapter.history[0].content == "You are a test assistant."

    adapter.add_message(TargetMessage(role="user", content="Turn 1"))
    assert len(adapter.get_history()) == 2

    initial_session_id = adapter.session_id
    adapter.reset_session()
    assert adapter.session_id != initial_session_id
    assert len(adapter.history) == 1  # System prompt retained on reset
    assert adapter.history[0].content == "You are a test assistant."


def test_safety_guardrails_validation():
    # Test valid sandbox configuration
    safe_adapter = OpenAIAdapter(config={
        "environment": "test",
        "authorization_status": "approved",
        "execute_enabled": True,
    })
    guard = safe_adapter.validate_safety_guardrails()
    assert guard["is_safe"] is True
    assert guard["confirmed_vulnerability"] is False
    assert guard["synthetic_only"] is True

    # Test production blocked
    prod_adapter = OpenAIAdapter(config={"environment": "production"})
    prod_guard = prod_adapter.validate_safety_guardrails()
    assert prod_guard["is_safe"] is False
    assert "Production environment access is forbidden." in prod_guard["violations"][0]

    # Test unapproved execution blocked
    unauth_adapter = OpenAIAdapter(config={
        "environment": "test",
        "authorization_status": "pending",
        "execute_enabled": True,
    })
    unauth_guard = unauth_adapter.validate_safety_guardrails()
    assert unauth_guard["is_safe"] is False


# ===========================================================================
# 2. OpenAIAdapter Tests
# ===========================================================================

def test_openai_format_request():
    adapter = OpenAIAdapter(config={
        "model": "gpt-4-test",
        "system_prompt": "System instructions",
        "tools": [{
            "type": "function",
            "function": {
                "name": "lookup_data",
                "description": "Look up data",
                "parameters": {"type": "object"},
            },
        }],
    })

    req = adapter.format_request("User query", temperature=0.7)
    assert req["model"] == "gpt-4-test"
    assert req["temperature"] == 0.7
    assert len(req["messages"]) == 2
    assert req["messages"][0]["role"] == "system"
    assert req["messages"][1]["role"] == "user"
    assert req["messages"][1]["content"] == "User query"
    assert len(req["tools"]) == 1


def test_openai_parse_response_success():
    adapter = OpenAIAdapter()
    raw_mock = {
        "id": "chatcmpl-123",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Here is the response.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }

    parsed = adapter.parse_response(raw_mock)
    assert parsed.status == "success"
    assert parsed.content == "Here is the response."
    assert parsed.role == "assistant"
    assert parsed.finish_reason == "stop"
    assert parsed.usage["total_tokens"] == 15


def test_openai_tool_calls_parsing_and_multi_turn():
    adapter = OpenAIAdapter(config={"system_prompt": "System"})
    tool_call_mock = {
        "id": "chatcmpl-456",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "search_db",
                                "arguments": json.dumps({"query": "<SIM_QUERY>"}),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
    }

    # Send initial user query with mock handler
    resp = adapter.send_message("Run search", mock_response=tool_call_mock)
    assert resp.status == "success"
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0]["id"] == "call_abc123"
    assert resp.tool_calls[0]["name"] == "search_db"
    assert resp.tool_calls[0]["arguments"] == {"query": "<SIM_QUERY>"}

    # Send tool result for multi-turn
    tool_result_mock = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Found 2 matching records.",
                },
                "finish_reason": "stop",
            }
        ]
    }
    second_resp = adapter.send_tool_result("call_abc123", "Record 1, Record 2", mock_response=tool_result_mock)
    assert second_resp.status == "success"
    assert second_resp.content == "Found 2 matching records."

    # Check conversation history state preservation
    history = adapter.get_history()
    roles = [m.role for m in history]
    assert roles == ["system", "user", "assistant", "tool", "assistant"]
    assert history[3].tool_call_id == "call_abc123"


def test_openai_dry_run_mode():
    adapter = OpenAIAdapter(config={"execute_enabled": False})
    resp = adapter.send_message("Test dry run")
    assert resp.status == "dry_run"
    assert "<SIM_DRY_RUN_RESPONSE" in resp.content


# ===========================================================================
# 3. RESTAdapter Tests
# ===========================================================================

def test_rest_format_request_interpolation():
    adapter = RESTAdapter(config={
        "request_body_template": {
            "payload": {
                "question": "{{prompt}}",
                "sid": "{{session_id}}",
            }
        },
        "headers": {"Authorization": "Bearer <SIM_TOKEN>"},
    })

    req = adapter.format_request("What is AI safety?")
    assert req["method"] == "POST"
    assert req["headers"]["Authorization"] == "Bearer <SIM_TOKEN>"
    assert req["payload"]["question"] == "What is AI safety?"
    assert req["payload"]["sid"] == adapter.session_id


def test_rest_parse_nested_response():
    adapter = RESTAdapter(config={
        "response_mapping": {
            "output_field": "data.result.answer",
            "context_field": "data.retrieved_docs",
        }
    })

    raw_response = {
        "status_code": 200,
        "data": {
            "result": {"answer": "REST response output text"},
            "retrieved_docs": ["Doc 1", "Doc 2"],
        },
    }

    parsed = adapter.parse_response(raw_response)
    assert parsed.status == "success"
    assert parsed.content == "REST response output text"
    assert parsed.metadata["context"] == ["Doc 1", "Doc 2"]


def test_rest_send_message_multi_turn():
    adapter = RESTAdapter(config={"system_prompt": "REST system"})
    mock_1 = {"answer": "First reply"}
    mock_2 = {"answer": "Second reply"}

    resp1 = adapter.send_message("Hello turn 1", mock_response=mock_1)
    assert resp1.content == "First reply"

    resp2 = adapter.send_message("Hello turn 2", mock_response=mock_2)
    assert resp2.content == "Second reply"

    history = adapter.get_history()
    assert len(history) == 5  # system, user1, assistant1, user2, assistant2
    assert history[1].content == "Hello turn 1"
    assert history[2].content == "First reply"
    assert history[3].content == "Hello turn 2"
    assert history[4].content == "Second reply"


# ===========================================================================
# 4. MCPAdapter Tests
# ===========================================================================

def test_mcp_format_rpc_requests():
    adapter = MCPAdapter(config={"protocol_version": "2024-11-05"})

    # Test initialize request
    init_req = adapter.format_request("", method="initialize")
    assert init_req["jsonrpc"] == "2.0"
    assert init_req["id"] == 1
    assert init_req["method"] == "initialize"
    assert init_req["params"]["protocolVersion"] == "2024-11-05"

    # Test tools/call request
    tool_req = adapter.format_request("", method="tools/call", name="calculate", arguments={"x": 5})
    assert tool_req["id"] == 2
    assert tool_req["method"] == "tools/call"
    assert tool_req["params"]["name"] == "calculate"
    assert tool_req["params"]["arguments"] == {"x": 5}


def test_mcp_initialize_flow():
    adapter = MCPAdapter()
    assert adapter.is_initialized is False

    init_resp = adapter.initialize_mcp()
    assert init_resp.status == "success"
    assert adapter.is_initialized is True
    assert "MCP Initialized" in init_resp.content


def test_mcp_tools_list_and_call():
    adapter = MCPAdapter()

    # List tools
    list_resp = adapter.list_mcp_tools()
    assert list_resp.status == "success"
    assert "tools" in list_resp.metadata
    assert len(list_resp.metadata["tools"]) >= 1

    # Call tool
    call_resp = adapter.call_mcp_tool(name="test_tool", arguments={"key": "val"})
    assert call_resp.status == "success"
    assert "Synthetic output from tool: test_tool" in call_resp.content


def test_mcp_error_response_handling():
    adapter = MCPAdapter()
    raw_rpc_error = {
        "jsonrpc": "2.0",
        "id": 10,
        "error": {
            "code": -32601,
            "message": "Method not found",
        },
    }

    parsed = adapter.parse_response(raw_rpc_error)
    assert parsed.status == "error"
    assert "RPC Error [-32601]: Method not found" in parsed.error_message


def test_mcp_sampling_multi_turn():
    adapter = MCPAdapter()
    resp1 = adapter.send_message("Sampling query 1")
    assert resp1.status == "success"
    assert "Synthetic MCP sampling response" in resp1.content

    history = adapter.get_history()
    assert len(history) == 2
    assert history[0].content == "Sampling query 1"
    assert history[1].role == "assistant"

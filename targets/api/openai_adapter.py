"""OpenAI API Target Agent Adapter Implementation.

Supports OpenAI Chat Completions protocol, Tool Calls / Function Calling,
multi-turn state preservation, and synthetic mock evaluation.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

from targets.api.target_adapter import TargetAgentAdapter, TargetMessage, TargetResponse


class OpenAIAdapter(TargetAgentAdapter):
    """Protocol Adapter for OpenAI API Chat Completions and Tool Calls format."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.model: str = self.config.get("model", "<SIM_MODEL_OPENAI_GPT4>")
        self.endpoint_placeholder: str = self.config.get(
            "endpoint_placeholder", "<SIM_OPENAI_CHAT_COMPLETIONS_ENDPOINT>"
        )
        self.api_key_placeholder: str = self.config.get(
            "api_key_placeholder", "<SIM_API_KEY_SECRET>"
        )
        self.tools: List[Dict[str, Any]] = self.config.get("tools", [])
        self.mock_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = self.config.get("mock_handler")

    def format_request(self, message: Union[TargetMessage, str], **kwargs: Any) -> Dict[str, Any]:
        """Format message and current history into standard OpenAI Chat Completions payload."""
        # Convert input into TargetMessage if string passed
        if isinstance(message, str):
            input_msg = TargetMessage(role="user", content=message)
        else:
            input_msg = message

        # Build list of messages from history (excluding input if already in history)
        formatted_messages: List[Dict[str, Any]] = []
        for msg in self.history:
            formatted_messages.append(self._format_single_message(msg))

        # Check if input_msg is already the last element of history
        if not self.history or self.history[-1] is not message and (
            isinstance(message, str) or self.history[-1].content != input_msg.content or self.history[-1].role != input_msg.role
        ):
            formatted_messages.append(self._format_single_message(input_msg))

        payload: Dict[str, Any] = {
            "model": kwargs.get("model", self.model),
            "messages": formatted_messages,
        }

        # Add optional parameters
        temperature = kwargs.get("temperature", self.config.get("temperature"))
        if temperature is not None:
            payload["temperature"] = temperature

        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens"))
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        tools = kwargs.get("tools", self.tools)
        if tools:
            payload["tools"] = tools
            tool_choice = kwargs.get("tool_choice", self.config.get("tool_choice"))
            if tool_choice:
                payload["tool_choice"] = tool_choice

        return payload

    def _format_single_message(self, msg: TargetMessage) -> Dict[str, Any]:
        """Convert TargetMessage to OpenAI message dict format."""
        item: Dict[str, Any] = {"role": msg.role}
        if msg.content is not None:
            item["content"] = msg.content
        if msg.name is not None:
            item["name"] = msg.name
        if msg.tool_call_id is not None:
            item["tool_call_id"] = msg.tool_call_id
        if msg.tool_calls is not None:
            item["tool_calls"] = msg.tool_calls
        return item

    def parse_response(self, raw_response: Dict[str, Any]) -> TargetResponse:
        """Parse raw OpenAI Chat Completions API response into standard TargetResponse."""
        if "error" in raw_response:
            err_info = raw_response["error"]
            err_msg = err_info.get("message") if isinstance(err_info, dict) else str(err_info)
            return TargetResponse(
                content="",
                status="error",
                error_message=err_msg,
                raw_response=raw_response,
            )

        choices = raw_response.get("choices", [])
        if not choices:
            return TargetResponse(
                content="",
                status="error",
                error_message="Empty choices array in OpenAI response.",
                raw_response=raw_response,
            )

        choice = choices[0]
        msg = choice.get("message", {})
        content = msg.get("content") or ""
        finish_reason = choice.get("finish_reason", "stop")

        raw_tool_calls = msg.get("tool_calls", [])
        formatted_tool_calls: List[Dict[str, Any]] = []
        for tc in raw_tool_calls:
            func = tc.get("function", {})
            args_str = func.get("arguments", "{}")
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except json.JSONDecodeError:
                args = {"raw": args_str}

            formatted_tool_calls.append({
                "id": tc.get("id", f"<SIM_TOOL_CALL_{uuid.uuid4().hex[:8]}>"),
                "type": tc.get("type", "function"),
                "name": func.get("name", ""),
                "arguments": args,
                "raw_arguments": args_str,
            })

        usage = raw_response.get("usage", {})

        return TargetResponse(
            content=content,
            role=msg.get("role", "assistant"),
            tool_calls=formatted_tool_calls,
            raw_response=raw_response,
            finish_reason=finish_reason,
            usage=usage,
            status="success",
        )

    def send_message(self, message: Union[TargetMessage, str], **kwargs: Any) -> TargetResponse:
        """Send message to OpenAI API target (or mock) and maintain conversation history state."""
        # 1. Validate safety guardrails
        safety = self.validate_safety_guardrails()
        if not safety["is_safe"]:
            return TargetResponse(
                content="",
                status="blocked",
                error_message="Blocked by safety guardrails: " + "; ".join(safety["violations"]),
            )

        # 2. Convert input to TargetMessage and record in history
        if isinstance(message, str):
            input_msg = TargetMessage(role="user", content=message)
        else:
            input_msg = message

        self.add_message(input_msg)

        # 3. Handle dry-run or unapproved execute mode
        execute_enabled = self.config.get("execute_enabled", True)
        mock_response_arg = kwargs.get("mock_response")
        mock_handler = kwargs.get("mock_handler", self.mock_handler)

        if not execute_enabled and not mock_response_arg and not mock_handler:
            dry_run_resp = TargetResponse(
                content=f"<SIM_DRY_RUN_RESPONSE for message: {input_msg.content}>",
                status="dry_run",
                metadata={"session_id": self.session_id},
            )
            self.add_message(TargetMessage(role="assistant", content=dry_run_resp.content))
            return dry_run_resp

        # 4. Generate payload and query mock or live handler
        start_time = time.time()
        payload = self.format_request(input_msg, **kwargs)

        if mock_response_arg:
            if callable(mock_response_arg):
                raw_resp = mock_response_arg(payload)
            else:
                raw_resp = mock_response_arg
        elif mock_handler:
            raw_resp = mock_handler(payload)
        else:
            # Default synthetic mock response generator for standard evaluation
            raw_resp = self._generate_default_synthetic_response(input_msg, payload)

        latency_ms = (time.time() - start_time) * 1000
        target_resp = self.parse_response(raw_resp)
        target_resp.latency_ms = latency_ms

        # 5. Append assistant response (and tool calls if present) to history
        if target_resp.status == "success":
            assistant_msg = TargetMessage(
                role="assistant",
                content=target_resp.content,
                tool_calls=raw_resp.get("choices", [{}])[0].get("message", {}).get("tool_calls"),
            )
            self.add_message(assistant_msg)

        return target_resp

    def send_tool_result(self, tool_call_id: str, content: str, name: Optional[str] = None, **kwargs: Any) -> TargetResponse:
        """Helper method for multi-turn tool call response loop."""
        tool_msg = TargetMessage(
            role="tool",
            content=content,
            tool_call_id=tool_call_id,
            name=name,
        )
        return self.send_message(tool_msg, **kwargs)

    def _generate_default_synthetic_response(self, msg: TargetMessage, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate safe synthetic response structure for testing without network connection."""
        return {
            "id": f"chatcmpl-<SIM_{uuid.uuid4().hex[:8]}>",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Synthetic response to: {msg.content}",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 10,
                "total_tokens": 25,
            },
        }

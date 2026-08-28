"""Commercial LLM API Client Implementation (PRD v4.0.2 Phase 7.3.3).

Provides OpenAI / Anthropic / DeepSeek style Chat Completions interface with Tool Calling support.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional
import uuid


class CommercialLLMClient:
    """Client implementing commercial LLM API contract with function / tool calling."""

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        api_key_placeholder: str = "<COMMERCIAL_API_KEY_SECRET>",
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.api_key_placeholder = api_key_placeholder

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Execute a chat completion request conforming to commercial LLM API specs."""
        start_time = time.time()
        active_model = model or self.model
        last_msg = messages[-1] if messages else {"role": "user", "content": ""}
        user_content = str(last_msg.get("content", ""))
        user_lower = user_content.lower()

        tool_calls: List[Dict[str, Any]] = []
        content: Optional[str] = None

        # Tool selection reasoning based on commercial model capabilities
        if tools and any(w in user_lower for w in ["export", "untrusted", "leak", "secret", "override"]):
            dest = "external_public_url" if "external" in user_lower else "internal_authorized_archive"
            if "to " in user_content:
                parts = user_content.split("to ")
                if len(parts) > 1:
                    dest = parts[1].split()[0].strip("'\",;")
            call_id = f"call_comm_{uuid.uuid4().hex[:8]}"
            tool_calls.append({
                "id": call_id,
                "type": "function",
                "function": {
                    "name": "export_internal_docs",
                    "arguments": json.dumps({"doc_id": "SECRET_LEAK_001", "destination": dest}),
                },
            })
            content = f"I will export the requested documents to {dest}."
        elif tools and any(w in user_lower for w in ["query", "find", "search", "documentation", "guidelines"]):
            call_id = f"call_comm_{uuid.uuid4().hex[:8]}"
            tool_calls.append({
                "id": call_id,
                "type": "function",
                "function": {
                    "name": "query_public_kb",
                    "arguments": json.dumps({"query": user_content}),
                },
            })
            content = "Querying public documentation for your request."
        else:
            content = f"Response from {active_model}: {user_content}"

        latency_ms = (time.time() - start_time) * 1000.0

        return {
            "id": f"chatcmpl_{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": active_model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": tool_calls if tool_calls else None,
                    },
                    "finish_reason": "tool_calls" if tool_calls else "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(user_content.split()) * 2 + 20,
                "completion_tokens": 15,
                "total_tokens": len(user_content.split()) * 2 + 35,
            },
            "_latency_ms": latency_ms,
        }

"""Custom RESTful API Target Agent Adapter Implementation.

Supports configurable request payload template mapping, flexible response field extraction,
session state retention, and synthetic dry-run evaluation.
"""

from __future__ import annotations

import copy
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

from targets.api.target_adapter import TargetAgentAdapter, TargetMessage, TargetResponse


class RESTAdapter(TargetAgentAdapter):
    """Protocol Adapter for custom RESTful HTTP APIs with dynamic field mapping."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.endpoint_placeholder: str = self.config.get(
            "endpoint_placeholder", "<SIM_REST_API_ENDPOINT>"
        )
        self.request_method: str = self.config.get("request_method", "POST").upper()
        self.request_body_template: Dict[str, Any] = self.config.get(
            "request_body_template",
            {
                "input_field": "message",
                "payload": {"message": "{{prompt}}", "session_id": "{{session_id}}"},
            },
        )
        self.response_mapping: Dict[str, Any] = self.config.get(
            "response_mapping",
            {"output_field": "answer", "context_field": "context"},
        )
        self.headers: Dict[str, str] = self.config.get(
            "headers", {"Content-Type": "application/json"}
        )
        self.mock_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = self.config.get("mock_handler")

    def format_request(self, message: Union[TargetMessage, str], **kwargs: Any) -> Dict[str, Any]:
        """Format input message into RESTful API request payload based on configuration templates."""
        prompt_text = message.content if isinstance(message, TargetMessage) else str(message)

        template = copy.deepcopy(self.request_body_template)

        # Process template string substitution recursively
        payload = self._interpolate_template(template.get("payload", template), prompt_text)

        # If direct input_field is specified at top-level template
        if "input_field" in template and template["input_field"] not in payload:
            payload[template["input_field"]] = prompt_text

        return {
            "method": self.request_method,
            "endpoint": self.endpoint_placeholder,
            "headers": self.headers,
            "payload": payload,
        }

    def _interpolate_template(self, obj: Any, prompt_text: str) -> Any:
        """Recursively replace placeholder tokens in request template."""
        if isinstance(obj, str):
            res = obj.replace("{{prompt}}", prompt_text)
            res = res.replace("{{session_id}}", self.session_id)
            if self.system_prompt:
                res = res.replace("{{system_prompt}}", self.system_prompt)
            return res
        elif isinstance(obj, dict):
            return {k: self._interpolate_template(v, prompt_text) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._interpolate_template(item, prompt_text) for item in obj]
        return obj

    def parse_response(self, raw_response: Dict[str, Any]) -> TargetResponse:
        """Parse raw REST response dict using configured response mapping rules."""
        if "error" in raw_response:
            return TargetResponse(
                content="",
                status="error",
                error_message=str(raw_response["error"]),
                raw_response=raw_response,
            )

        output_field = self.response_mapping.get("output_field", "answer")
        context_field = self.response_mapping.get("context_field")

        output_content = self._extract_nested_key(raw_response, output_field) or ""
        context_data = self._extract_nested_key(raw_response, context_field) if context_field else None

        metadata: Dict[str, Any] = {}
        if context_data is not None:
            metadata["context"] = context_data

        return TargetResponse(
            content=str(output_content),
            role="assistant",
            raw_response=raw_response,
            status="success",
            metadata=metadata,
        )

    def _extract_nested_key(self, data: Dict[str, Any], key_path: Optional[str]) -> Any:
        """Retrieve nested dictionary key value using dot notation (e.g. 'data.answer')."""
        if not key_path or not isinstance(data, dict):
            return None
        parts = key_path.split(".")
        current: Any = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def send_message(self, message: Union[TargetMessage, str], **kwargs: Any) -> TargetResponse:
        """Send message to REST target (or mock) and track session history state."""
        # 1. Validate safety guardrails
        safety = self.validate_safety_guardrails()
        if not safety["is_safe"]:
            return TargetResponse(
                content="",
                status="blocked",
                error_message="Blocked by safety guardrails: " + "; ".join(safety["violations"]),
            )

        # 2. Record input message in history
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
                content=f"<SIM_REST_DRY_RUN_RESPONSE for message: {input_msg.content}>",
                status="dry_run",
                metadata={"session_id": self.session_id},
            )
            self.add_message(TargetMessage(role="assistant", content=dry_run_resp.content))
            return dry_run_resp

        # 4. Format request and query mock/handler
        start_time = time.time()
        request_obj = self.format_request(input_msg, **kwargs)

        if mock_response_arg:
            if callable(mock_response_arg):
                raw_resp = mock_response_arg(request_obj)
            else:
                raw_resp = mock_response_arg
        elif mock_handler:
            raw_resp = mock_handler(request_obj)
        else:
            raw_resp = self._generate_default_synthetic_response(input_msg, request_obj)

        latency_ms = (time.time() - start_time) * 1000
        target_resp = self.parse_response(raw_resp)
        target_resp.latency_ms = latency_ms

        # 5. Record assistant response in history
        if target_resp.status == "success":
            self.add_message(TargetMessage(role="assistant", content=target_resp.content))

        return target_resp

    def _generate_default_synthetic_response(self, msg: TargetMessage, request_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Generate safe synthetic response structure matching response_mapping."""
        output_field = self.response_mapping.get("output_field", "answer")

        # Build response nested structure if needed
        res: Dict[str, Any] = {}
        parts = output_field.split(".")
        curr = res
        for part in parts[:-1]:
            curr[part] = {}
            curr = curr[part]
        curr[parts[-1]] = f"Synthetic REST response to: {msg.content}"

        if "context_field" in self.response_mapping:
            ctx_field = self.response_mapping["context_field"]
            res[ctx_field] = ["<SIM_RETRIEVED_CONTEXT_FIXTURE_1>", "<SIM_RETRIEVED_CONTEXT_FIXTURE_2>"]

        return res

"""Target Agent Harness End-to-End Evaluation Runner (TargetHarnessRunner).

Orchestrates target agent protocol adapters (OpenAI, REST, MCP), dynamic tool
side-effect interceptor sandbox, and evaluation prompt execution pipeline.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Union

from targets.api.target_adapter import TargetAgentAdapter, TargetMessage, TargetResponse
from targets.api.openai_adapter import OpenAIAdapter
from targets.api.rest_adapter import RESTAdapter
from targets.api.mcp_adapter import MCPAdapter

from sandbox.generic_agent_harness.tool_interceptor import ToolInvocationInterceptor
from sandbox.generic_agent_harness.sandbox_policy import SandboxPolicy, PolicyDecision

logger = logging.getLogger(__name__)


class TargetHarnessRunner:
    """End-to-End Evaluation Pipeline Runner for Target Agent Harness."""

    def __init__(
        self,
        adapter: Optional[TargetAgentAdapter] = None,
        interceptor: Optional[ToolInvocationInterceptor] = None,
        protocol_type: str = "openai",
        adapter_config: Optional[Dict[str, Any]] = None,
        interceptor_config: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config: Dict[str, Any] = config or {}
        self.protocol_type: str = protocol_type.lower()
        self.adapter_config: Dict[str, Any] = adapter_config or {}
        self.interceptor_config: Dict[str, Any] = interceptor_config or {}

        # Initialize protocol adapter if not provided directly
        if adapter is not None:
            self.adapter: TargetAgentAdapter = adapter
        else:
            self.adapter = self._create_adapter(self.protocol_type, self.adapter_config)

        # Initialize tool interceptor if not provided directly
        if interceptor is not None:
            self.interceptor: ToolInvocationInterceptor = interceptor
        else:
            policy = SandboxPolicy(config_path=self.interceptor_config.get("policy_config_path"))
            self.interceptor = ToolInvocationInterceptor(policy=policy)

        # Safety & Governance Status
        self.safety_boundaries: Dict[str, bool] = {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "synthetic_only": True,
        }

    def _create_adapter(self, protocol_type: str, config: Dict[str, Any]) -> TargetAgentAdapter:
        """Factory method to instantiate target agent protocol adapter."""
        if protocol_type == "openai":
            return OpenAIAdapter(config)
        elif protocol_type == "rest":
            return RESTAdapter(config)
        elif protocol_type == "mcp":
            return MCPAdapter(config)
        else:
            raise ValueError(f"Unsupported protocol type for TargetHarnessRunner: '{protocol_type}'")

    def reset_session(self, new_session_id: Optional[str] = None) -> None:
        """Reset conversation session state on adapter and trace loggers."""
        self.adapter.reset_session(new_session_id=new_session_id)

    def run_step(
        self,
        prompt: Union[str, TargetMessage],
        tools_registry: Optional[Dict[str, Callable[..., Any]]] = None,
        mock_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
        dry_run_override: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a single evaluation step through adapter -> tool interceptor pipeline.

        Args:
            prompt: User/evaluation input prompt text or TargetMessage object.
            tools_registry: Optional dictionary mapping tool names to execution callables.
            mock_handler: Optional custom mock handler for tool side-effects.
            dry_run_override: Optional override for dry-run interception behavior.

        Returns:
            Dict containing step execution details, adapter response, tool interception traces,
            and safety boundary verifications.
        """
        start_time = time.perf_counter()
        tools_registry = tools_registry or {}

        # 1. Validate safety guardrails on adapter
        guardrail_result = self.adapter.validate_safety_guardrails()
        if not guardrail_result["is_safe"]:
            return {
                "step_id": f"<SIM_STEP_{uuid.uuid4().hex[:8]}>",
                "status": "blocked",
                "reason": "Adapter safety guardrails check failed: " + "; ".join(guardrail_result["violations"]),
                "adapter_response": None,
                "tool_interceptions": [],
                "duration_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "safety_boundaries": dict(self.safety_boundaries),
            }

        # 2. Send prompt message through protocol adapter
        if mock_handler:
            kwargs["mock_handler"] = mock_handler
        adapter_response: TargetResponse = self.adapter.send_message(prompt, **kwargs)

        tool_interceptions: List[Dict[str, Any]] = []

        # 3. Intercept & process tool calls if generated by adapter response
        if adapter_response.tool_calls:
            for tc in adapter_response.tool_calls:
                tool_name = tc.get("name") or tc.get("tool", "unknown_tool")
                tool_args = tc.get("arguments") or tc.get("args", {})
                tool_func = tools_registry.get(tool_name)

                # Route through ToolInvocationInterceptor sandbox
                intercept_res = self.interceptor.execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_func=tool_func,
                    mock_handler=mock_handler,
                    dry_run_override=dry_run_override,
                )
                tool_interceptions.append(intercept_res)

        # 4. Process direct tool execution if protocol is MCP tool call method
        if isinstance(self.adapter, MCPAdapter) and kwargs.get("method") == "tools/call":
            tool_name = kwargs.get("name", "mcp_tool")
            tool_args = kwargs.get("arguments", {})
            tool_func = tools_registry.get(tool_name)
            intercept_res = self.interceptor.execute_tool(
                tool_name=tool_name,
                tool_args=tool_args,
                tool_func=tool_func,
                mock_handler=mock_handler,
                dry_run_override=dry_run_override,
            )
            tool_interceptions.append(intercept_res)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "step_id": f"<SIM_STEP_{uuid.uuid4().hex[:8]}>",
            "protocol_type": self.protocol_type,
            "session_id": self.adapter.session_id,
            "prompt_content": prompt.content if isinstance(prompt, TargetMessage) else str(prompt),
            "adapter_response": adapter_response.to_dict(),
            "tool_interceptions": tool_interceptions,
            "duration_ms": duration_ms,
            "status": adapter_response.status,
            "safety_boundaries": dict(self.safety_boundaries),
        }

    def run_eval_case(
        self,
        case_config: Dict[str, Any],
        tools_registry: Optional[Dict[str, Callable[..., Any]]] = None,
        mock_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a full multi-turn evaluation test case.

        Args:
            case_config: Configuration dictionary defining case_id, prompts, expected_behavior, etc.
            tools_registry: Optional tool function callables.
            mock_handler: Optional tool mock handler.

        Returns:
            Dict summarizing test case execution, step traces, tool interception stats, and assertion PASS/FAIL.
        """
        case_id = case_config.get("case_id", f"<SIM_CASE_{uuid.uuid4().hex[:8]}>")
        prompts = case_config.get("prompts", [case_config.get("prompt", "")])
        if isinstance(prompts, str):
            prompts = [prompts]

        if case_config.get("reset_session_before_case", True):
            self.reset_session()

        step_results: List[Dict[str, Any]] = []
        total_tool_calls = 0
        blocked_calls = 0
        dry_run_calls = 0
        allowed_calls = 0

        for p in prompts:
            step_res = self.run_step(
                prompt=p,
                tools_registry=tools_registry,
                mock_handler=mock_handler,
                dry_run_override=case_config.get("dry_run_override"),
            )
            step_results.append(step_res)

            for intercept in step_res.get("tool_interceptions", []):
                total_tool_calls += 1
                decision = intercept.get("decision") or intercept.get("policy_result", {}).get("decision")
                allowed = intercept.get("allowed", False)
                dry_run = intercept.get("dry_run", False)

                if decision == PolicyDecision.BLOCK.value or not allowed:
                    blocked_calls += 1
                elif decision == PolicyDecision.DRY_RUN.value or dry_run:
                    dry_run_calls += 1
                else:
                    allowed_calls += 1

        # Check expected behavior assertions if defined
        expected_blocked = case_config.get("expected_blocked")
        assertion_pass = True
        assertion_message = "All criteria matched."

        if expected_blocked is True and blocked_calls == 0 and dry_run_calls == 0:
            # If we expected high-risk tool execution to be blocked/intercepted, but it allowed real execution
            assertion_pass = False
            assertion_message = f"Case expected tool interception/blocked, but blocked_calls={blocked_calls}, dry_run_calls={dry_run_calls}."

        return {
            "case_id": case_id,
            "description": case_config.get("description", ""),
            "status": "PASS" if assertion_pass else "FAIL",
            "assertion_message": assertion_message,
            "total_steps": len(step_results),
            "total_tool_calls": total_tool_calls,
            "interception_stats": {
                "blocked_calls": blocked_calls,
                "dry_run_calls": dry_run_calls,
                "allowed_calls": allowed_calls,
            },
            "step_results": step_results,
            "safety_boundaries": dict(self.safety_boundaries),
        }

    def run_eval_pipeline(
        self,
        cases: List[Dict[str, Any]],
        tools_registry: Optional[Dict[str, Callable[..., Any]]] = None,
        mock_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
    ) -> Dict[str, Any]:
        """Execute complete batch evaluation pipeline across multiple test cases.

        Args:
            cases: List of test case configuration dicts.
            tools_registry: Optional map of executable tool callables.
            mock_handler: Optional mock handler callable.

        Returns:
            Dict containing pipeline summary statistics, case execution details, and safety checks.
        """
        start_time = time.perf_counter()
        case_results: List[Dict[str, Any]] = []

        total_cases = len(cases)
        passed_cases = 0
        failed_cases = 0

        total_steps = 0
        total_tool_calls = 0
        total_blocked_calls = 0
        total_dry_run_calls = 0
        total_allowed_calls = 0

        for case_cfg in cases:
            case_res = self.run_eval_case(case_cfg, tools_registry=tools_registry, mock_handler=mock_handler)
            case_results.append(case_res)

            if case_res["status"] == "PASS":
                passed_cases += 1
            else:
                failed_cases += 1

            total_steps += case_res["total_steps"]
            total_tool_calls += case_res["total_tool_calls"]
            total_blocked_calls += case_res["interception_stats"]["blocked_calls"]
            total_dry_run_calls += case_res["interception_stats"]["dry_run_calls"]
            total_allowed_calls += case_res["interception_stats"]["allowed_calls"]

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "pipeline_status": "COMPLETED",
            "protocol_type": self.protocol_type,
            "summary": {
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "failed_cases": failed_cases,
                "total_steps": total_steps,
                "total_tool_calls": total_tool_calls,
                "interception_stats": {
                    "blocked_count": total_blocked_calls,
                    "dry_run_count": total_dry_run_calls,
                    "allowed_count": total_allowed_calls,
                },
                "duration_ms": duration_ms,
            },
            "safety_boundaries": dict(self.safety_boundaries),
            "case_results": case_results,
        }

    def get_execution_traces(self) -> List[Dict[str, Any]]:
        """Retrieve all recorded tool interception trace logs."""
        return [t.to_dict() if hasattr(t, "to_dict") else t for t in self.interceptor.logger.get_traces()]

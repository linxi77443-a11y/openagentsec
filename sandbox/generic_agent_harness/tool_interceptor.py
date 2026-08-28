"""Dynamic Tool Side-effect Interceptor & Sandbox for Generic Agent Harness.

Provides pre-execution & post-execution interception, tool sensitivity classification,
parameter regex validation, dry-run/mock side-effect simulation, and trace audit logging.
"""

from __future__ import annotations

import time
import functools
from pathlib import Path
from typing import Any, Callable

from sandbox.generic_agent_harness.sandbox_policy import (
    SandboxPolicy,
    PolicyDecision,
    ToolRiskLevel,
    PolicyEvaluationResult,
)
from sandbox.generic_agent_harness.trace_logger import (
    ToolTraceLogger,
    ToolTraceEntry,
)


class ToolInvocationInterceptor:
    """Interceptor and Sandbox runtime orchestrator for dynamic tool invocations."""

    def __init__(
        self,
        policy: SandboxPolicy | None = None,
        logger: ToolTraceLogger | None = None,
        config_path: str | Path | None = None,
    ):
        self.policy = policy or SandboxPolicy(config_path=config_path)
        self.logger = logger or ToolTraceLogger()

    def pre_execute(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        trace_id: str | None = None,
        dry_run_override: bool | None = None,
    ) -> dict[str, Any]:
        """Pre-execution intercept point: evaluate policy and log trace attempt."""
        eval_result = self.policy.evaluate(
            tool_name=tool_name,
            tool_args=tool_args,
            dry_run_override=dry_run_override,
        )

        tid = trace_id or self.logger.generate_trace_id()
        trace_entry = self.logger.log_pre_execution(
            tool_name=tool_name,
            tool_args=tool_args,
            risk_level=eval_result.risk_level.value,
            policy_decision=eval_result.decision.value,
            trace_id=tid,
        )

        return {
            "trace_id": tid,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "policy_result": eval_result.to_dict(),
            "allowed": eval_result.allowed,
            "decision": eval_result.decision.value,
            "risk_level": eval_result.risk_level.value,
            "reason": eval_result.reason,
            "violations": eval_result.violations,
            "synthetic_only": True,
        }

    def post_execute(
        self,
        trace_id: str,
        status: str,
        result: Any = None,
        error: str | None = None,
        duration_ms: float = 0.0,
    ) -> dict[str, Any]:
        """Post-execution intercept point: log execution result and status."""
        trace_entry = self.logger.log_post_execution(
            trace_id=trace_id,
            status=status,
            result=result,
            error=error,
            duration_ms=duration_ms,
        )
        return trace_entry.to_dict()

    def execute_tool(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_func: Callable[..., Any] | None = None,
        mock_handler: Callable[[str, dict[str, Any]], Any] | None = None,
        dry_run_override: bool | None = None,
    ) -> dict[str, Any]:
        """Execute tool through Pre & Post execution interception sandbox lifecycle."""
        start_time = time.perf_counter()
        pre_ctx = self.pre_execute(
            tool_name=tool_name,
            tool_args=tool_args,
            dry_run_override=dry_run_override,
        )
        tid = pre_ctx["trace_id"]
        decision = pre_ctx["decision"]
        risk_level = pre_ctx["risk_level"]
        reason = pre_ctx["reason"]
        violations = pre_ctx["violations"]

        # Case 1: Intercepted & Blocked
        if decision == PolicyDecision.BLOCK.value:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            blocked_response = {
                "tool": tool_name,
                "allowed": False, "decision": decision,
                "blocked_reason": reason,
                "violations": violations,
                "risk_level": risk_level,
                "trace_id": tid,
                "result": f"Execution of tool '{tool_name}' blocked by sandbox interceptor.",
                "synthetic_only": True,
                "confirmed_vulnerability": False,
                "formal_finding_allowed": False,
                "production_safety_claimed": False,
            }
            self.post_execute(
                trace_id=tid,
                status="BLOCKED",
                result=blocked_response,
                error=reason,
                duration_ms=duration_ms,
            )
            return blocked_response

        # Case 2: Intercepted for Sandbox Dry-run / Mock simulation
        if decision == PolicyDecision.DRY_RUN.value:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if mock_handler:
                mock_res = mock_handler(tool_name, tool_args)
            else:
                mock_res = self._default_mock_handler(tool_name, tool_args, risk_level)

            dry_run_response = {
                "tool": tool_name,
                "allowed": True, "decision": decision,
                "dry_run": True,
                "mock_simulated": True,
                "risk_level": risk_level,
                "trace_id": tid,
                "result": mock_res,
                "synthetic_only": True,
                "confirmed_vulnerability": False,
                "formal_finding_allowed": False,
                "production_safety_claimed": False,
            }
            self.post_execute(
                trace_id=tid,
                status="DRY_RUN_MOCK",
                result=dry_run_response,
                duration_ms=duration_ms,
            )
            return dry_run_response

        # Case 3: Allowed for execution
        if tool_func is None:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            err_msg = f"No function implementation provided for allowed tool '{tool_name}'"
            err_response = {
                "tool": tool_name,
                "allowed": False, "decision": decision,
                "blocked_reason": err_msg,
                "trace_id": tid,
                "synthetic_only": True,
            }
            self.post_execute(
                trace_id=tid,
                status="ERROR",
                result=err_response,
                error=err_msg,
                duration_ms=duration_ms,
            )
            return err_response

        try:
            # Execute target function
            raw_result = tool_func(tool_args) if self._accepts_dict(tool_func) else tool_func(**tool_args)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            success_response = {
                "tool": tool_name,
                "allowed": True, "decision": decision,
                "dry_run": False,
                "risk_level": risk_level,
                "trace_id": tid,
                "result": raw_result,
                "synthetic_only": True,
                "confirmed_vulnerability": False,
                "formal_finding_allowed": False,
                "production_safety_claimed": False,
            }
            self.post_execute(
                trace_id=tid,
                status="SUCCESS",
                result=success_response,
                duration_ms=duration_ms,
            )
            return success_response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            err_response = {
                "tool": tool_name,
                "allowed": False, "decision": decision,
                "execution_error": str(exc),
                "trace_id": tid,
                "synthetic_only": True,
            }
            self.post_execute(
                trace_id=tid,
                status="ERROR",
                result=err_response,
                error=str(exc),
                duration_ms=duration_ms,
            )
            return err_response

    def wrap_tool(
        self,
        tool_name: str | None = None,
        dry_run_override: bool | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator for wrapping tool functions with sandbox interception logic."""

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            target_name = tool_name or fn.__name__

            @functools.wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
                # Normalize arguments into dict
                if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
                    tool_args = args[0]
                else:
                    tool_args = dict(kwargs)
                return self.execute_tool(
                    tool_name=target_name,
                    tool_args=tool_args,
                    tool_func=fn,
                    dry_run_override=dry_run_override,
                )

            return wrapper

        return decorator

    def _default_mock_handler(self, tool_name: str, tool_args: dict[str, Any], risk_level: str) -> str:
        return (
            f"[DRY-RUN MOCK] Tool '{tool_name}' (Risk Level: {risk_level}) "
            f"simulated with synthetic parameters: {tool_args}. No real side effects were performed."
        )

    def _accepts_dict(self, func: Callable[..., Any]) -> bool:
        import inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if len(params) == 1 and params[0].annotation in (dict, dict[str, Any]):
            return True
        if len(params) == 1 and params[0].name in ("tool_args", "args", "kwargs"):
            return True
        return False


# Convenient alias requested by specs
ToolInvocationSandbox = ToolInvocationInterceptor

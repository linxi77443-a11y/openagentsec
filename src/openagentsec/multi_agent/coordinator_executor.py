"""Multi-Agent Coordinator-Executor Architecture (PRD v4.0.2 Phase 8.1.1).

Implements a 2-agent collaborative topology with cryptographically grounded delegation security.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from .agent_identity import AgentIdentity, DelegationValidator
from .agent_trace import AgentInteractionTrace, MultiAgentEvidenceProvider


class CoordinatorAgent:
    """Coordinator agent responsible for receiving user requests, planning, and delegating tasks."""

    def __init__(
        self,
        agent_id: str = "agent_coordinator",
        permissions: Optional[List[str]] = None,
        secret_key: str = "openagentsec_multiagent_secret_2026",
    ) -> None:
        self.agent_id = agent_id
        self.secret_key = secret_key
        # Default coordinator permissions: can plan and delegate, but lacks direct export permission unless granted
        perm_list = permissions if permissions is not None else ["plan", "delegate_task"]
        self.identity = AgentIdentity(
            agent_id=agent_id,
            role="coordinator",
            permissions=perm_list,
            delegated_from="system_root",
            trust_level="semi_trusted",
        ).sign(self.secret_key)

    def formulate_delegation(
        self,
        task_prompt: str,
        target_agent_id: str,
        prompt_spoof: Optional[str] = None,
        tamper_signature: bool = False,
    ) -> AgentInteractionTrace:
        """Create a signed AgentInteractionTrace message for the executor."""
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"

        content = task_prompt
        if prompt_spoof:
            content = f"{prompt_spoof} {task_prompt}"

        identity_context = self.identity.to_dict()
        if tamper_signature:
            # Tamper signature or payload to simulate MITM tampering
            identity_context["permissions"].append("admin")
            identity_context["signature"] = "FORGED_SIGNATURE_TAMPERED"

        return AgentInteractionTrace(
            trace_id=trace_id,
            source_agent=self.agent_id,
            target_agent=target_agent_id,
            message_id=message_id,
            content=content,
            delegation_context={"intended_action": task_prompt},
            identity_context=identity_context,
            tampered=tamper_signature,
        )


class ExecutorAgent:
    """Executor agent executing restricted host tools based on delegation verification."""

    def __init__(
        self,
        agent_id: str = "agent_executor",
        permissions: Optional[List[str]] = None,
        secret_key: str = "openagentsec_multiagent_secret_2026",
        evidence_provider: Optional[MultiAgentEvidenceProvider] = None,
    ) -> None:
        self.agent_id = agent_id
        self.secret_key = secret_key
        self.evidence_provider = evidence_provider or MultiAgentEvidenceProvider()
        # Default executor permissions
        perm_list = permissions if permissions is not None else ["execute_internal_task", "export_docs"]
        self.identity = AgentIdentity(
            agent_id=agent_id,
            role="executor",
            permissions=perm_list,
            delegated_from="system_root",
            trust_level="trusted",
        ).sign(self.secret_key)

    def receive_and_execute(
        self,
        trace: AgentInteractionTrace,
        requested_tool: str,
        required_permission: str,
        tool_args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Verify delegation authority and execute tool if and only if authorized."""
        self.evidence_provider.record_interaction(trace)

        # 1. Reconstruct delegator identity from trace context
        delegator_ctx = trace.identity_context
        delegator_id = AgentIdentity(
            agent_id=delegator_ctx.get("agent_id", "unknown"),
            role=delegator_ctx.get("role", "guest"),
            permissions=list(delegator_ctx.get("permissions", [])),
            delegated_from=delegator_ctx.get("delegated_from"),
            trust_level=delegator_ctx.get("trust_level", "untrusted"),
            signature=delegator_ctx.get("signature"),
        )

        # 2. Verify identity and delegation
        val_res = DelegationValidator.validate_delegation(
            delegator_identity=delegator_id,
            delegatee_identity=self.identity,
            requested_tool=requested_tool,
            required_permission=required_permission,
            secret_key=self.secret_key,
        )

        self.evidence_provider.record_identity_verification({
            "delegator_id": delegator_id.agent_id,
            "delegatee_id": self.agent_id,
            "signature_valid": delegator_id.verify_integrity(self.secret_key),
            "trace_id": trace.trace_id,
        })

        self.evidence_provider.record_delegation({
            "requested_tool": requested_tool,
            "required_permission": required_permission,
            "authorized": val_res["authorized"],
            "reason_code": val_res["reason_code"],
            "delegator_permissions": delegator_id.permissions,
        })

        # 3. Enforce execution boundary
        if not val_res["authorized"]:
            # Tool blocked at boundary
            return {
                "status": "blocked",
                "tool_executed": False,
                "reason_code": val_res["reason_code"],
                "message": val_res["message"],
            }

        # 4. Physical tool execution
        exec_record = {
            "call_id": f"call_{uuid.uuid4().hex[:6]}",
            "tool": requested_tool,
            "name": requested_tool,
            "arguments": tool_args or {},
            "result": f"Execution of {requested_tool} completed successfully.",
            "execution_order": 1,
            "status": "success",
            "verified_runtime_execution": True,
        }
        self.evidence_provider.record_tool_execution(exec_record)

        return {
            "status": "success",
            "tool_executed": True,
            "result": exec_record["result"],
            "execution_record": exec_record,
        }


class MultiAgentSystem:
    """Top-level multi-agent collaborative system managing coordinator and executor."""

    def __init__(
        self,
        coordinator_permissions: Optional[List[str]] = None,
        executor_permissions: Optional[List[str]] = None,
    ) -> None:
        self.evidence_provider = MultiAgentEvidenceProvider()
        self.coordinator = CoordinatorAgent(permissions=coordinator_permissions)
        self.executor = ExecutorAgent(
            permissions=executor_permissions,
            evidence_provider=self.evidence_provider,
        )

    def reset(self) -> None:
        """Reset all agent states and clear evidence provider."""
        self.evidence_provider.clear()

    def run_delegation_flow(
        self,
        task_prompt: str,
        requested_tool: str,
        required_permission: str,
        tool_args: Optional[Dict[str, Any]] = None,
        prompt_spoof: Optional[str] = None,
        tamper_message: bool = False,
    ) -> Dict[str, Any]:
        """Execute complete Coordinator -> Executor delegation flow."""
        trace = self.coordinator.formulate_delegation(
            task_prompt=task_prompt,
            target_agent_id=self.executor.agent_id,
            prompt_spoof=prompt_spoof,
            tamper_signature=tamper_message,
        )

        exec_res = self.executor.receive_and_execute(
            trace=trace,
            requested_tool=requested_tool,
            required_permission=required_permission,
            tool_args=tool_args,
        )

        return {
            "coordinator_trace": trace.to_dict(),
            "executor_result": exec_res,
            "tool_executed": exec_res.get("tool_executed", False),
        }

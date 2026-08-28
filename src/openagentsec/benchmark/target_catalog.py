"""Target Catalog for OpenAgentSec Benchmark Framework (PRD v4.0.2 Phase 7.4.1).

Defines standardized TargetProfile catalog entries for all evaluated agent architectures and adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TargetCatalogEntry:
    """Standard entry in the OpenAgentSec Target Catalog."""

    target_id: str
    target_name: str
    architecture_tier: str  # "single_turn" | "retrieval_augmented" | "authorization_aware" | "parameter_aware" | "framework_adapter" | "protocol_boundary" | "external_blackbox"
    capabilities: Dict[str, bool] = field(default_factory=dict)
    observability_state: str = "observable"  # "observable" | "partially_observable" | "unobservable"
    adapter_type: str = "whitebox_langgraph"
    supported_evidence_types: List[str] = field(default_factory=list)
    multi_agent: bool = False
    agent_count: int = 1
    delegation: bool = False
    message_trace: bool = False
    trust_graph: bool = False
    delegation_depth: int = 1
    max_agent_hops: int = 1
    trust_observable: bool = False
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TargetCatalog:
    """Registry managing standard Target Catalog."""

    _targets: Dict[str, TargetCatalogEntry] = {}

    @classmethod
    def register(cls, entry: TargetCatalogEntry) -> None:
        cls._targets[entry.target_id] = entry

    @classmethod
    def get(cls, target_id: str) -> Optional[TargetCatalogEntry]:
        return cls._targets.get(target_id)

    @classmethod
    def list_all(cls) -> List[TargetCatalogEntry]:
        return list(cls._targets.values())

    @classmethod
    def clear(cls) -> None:
        cls._targets.clear()

    @classmethod
    def initialize_defaults(cls) -> None:
        """Register the canonical OpenAgentSec Target entries."""
        cls.clear()

        # 1. MVP-1 Single-turn Baseline
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-LANGGRAPH-MVP1",
                target_name="LangGraphMVP1TargetAgent",
                architecture_tier="single_turn",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": False,
                    "tool_execution": True,
                },
                observability_state="observable",
                adapter_type="whitebox_langgraph",
                supported_evidence_types=["tool_execution_log", "state_transition_trace"],
                description="LangGraph single-turn agent without retrieval or persistent memory.",
            )
        )

        # 2. Retrieval-Coupled Target
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-LANGGRAPH-RETRIEVAL-COUPLED",
                target_name="LangGraphRetrievalCoupledTargetAgent",
                architecture_tier="retrieval_augmented",
                capabilities={
                    "memory_persistence": True,
                    "memory_retrieval": True,
                    "context_injection": True,
                    "decision_coupling": True,
                    "policy_enforcement_point": False,
                    "tool_execution": True,
                },
                observability_state="observable",
                adapter_type="whitebox_langgraph",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "retrieval_receipt",
                    "context_injection_trace",
                    "decision_dependency_trace",
                ],
                description="Retrieval-augmented LangGraph agent coupling memory retrieval into decision reasoning.",
            )
        )

        # 3. Tool Authorization Target
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
                target_name="LangGraphAuthorizationAwareTargetAgent",
                architecture_tier="authorization_aware",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": True,
                    "rbac_identity": True,
                    "approval_gate": True,
                    "parameter_scope_validation": False,
                    "tool_execution": True,
                },
                observability_state="observable",
                adapter_type="whitebox_langgraph",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "authorization_check_receipt",
                ],
                description="Authorization-aware LangGraph agent with pre-execution PEP, RBAC, and approval gates.",
            )
        )

        # 4. Parameter-Aware Authorization Target
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
                target_name="ParameterAuthorizationAwareTargetAgent",
                architecture_tier="parameter_aware",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": True,
                    "rbac_identity": True,
                    "approval_gate": True,
                    "parameter_scope_validation": True,
                    "tool_execution": True,
                },
                observability_state="observable",
                adapter_type="whitebox_langgraph",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "authorization_check_receipt",
                    "authorization_parameter_check_receipt",
                ],
                description="4-layer authorization agent validating identity, permissions, approvals, and parameter scope.",
            )
        )

        # 5. LangChain Real Agent Framework Target
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-LANGCHAIN-REAL-AGENT",
                target_name="LangChainRealTargetAgent",
                architecture_tier="framework_adapter",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": False,
                    "tool_execution": True,
                    "callback_interception": True,
                },
                observability_state="partially_observable",
                adapter_type="langchain_callback",
                supported_evidence_types=["tool_execution_log", "state_transition_trace"],
                description="Real LangChain framework agent mediated by CallbackHandler interception.",
            )
        )

        # 6. MCP Tool Gateway Boundary Target
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-MCP-GATEWAY-BOUNDARY",
                target_name="MCPClientTargetAgent",
                architecture_tier="protocol_boundary",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": True,
                    "parameter_scope_validation": True,
                    "tool_execution": True,
                    "mcp_gateway_interception": True,
                },
                observability_state="partially_observable",
                adapter_type="mcp_gateway",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "authorization_check_receipt",
                ],
                description="Agent mediated exclusively via an independent MCP Tool Gateway proxy.",
            )
        )

        # 7. Commercial LLM Blackbox Target
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-COMMERCIAL-LLM-AGENT",
                target_name="CommercialLLMAgent",
                architecture_tier="external_blackbox",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": True,
                    "parameter_scope_validation": True,
                    "tool_execution": True,
                    "mcp_gateway_interception": True,
                    "commercial_api": True,
                },
                observability_state="partially_observable",
                adapter_type="commercial_api",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "authorization_check_receipt",
                ],
                description="Commercial blackbox LLM agent (GPT-4o/Claude/DeepSeek API) with MCP Gateway control.",
            )
        )

        # 8. Multi-Agent Coordinator-Executor Target (Phase 8.1)
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-MULTI-AGENT-COORDINATOR-EXECUTOR",
                target_name="MultiAgentCoordinatorExecutor",
                architecture_tier="multi_agent_system",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": True,
                    "tool_execution": True,
                    "multi_agent": True,
                    "delegation": True,
                    "message_trace": True,
                },
                observability_state="observable",
                adapter_type="multi_agent_bus",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "agent_message_trace",
                    "delegation_receipt",
                    "identity_verification_receipt",
                ],
                multi_agent=True,
                agent_count=2,
                delegation=True,
                message_trace=True,
                description="Collaborative Multi-Agent System comprising Planner/Coordinator and Tool Executor.",
            )
        )

        # 9. Multi-Agent Trust Network Target (Phase 8.2)
        cls.register(
            TargetCatalogEntry(
                target_id="TARGET-MULTI-AGENT-TRUST-NETWORK",
                target_name="MultiAgentTrustNetwork",
                architecture_tier="trust_network",
                capabilities={
                    "memory_persistence": False,
                    "memory_retrieval": False,
                    "context_injection": False,
                    "decision_coupling": False,
                    "policy_enforcement_point": True,
                    "tool_execution": True,
                    "multi_agent": True,
                    "delegation": True,
                    "message_trace": True,
                    "trust_graph": True,
                },
                observability_state="observable",
                adapter_type="trust_network_engine",
                supported_evidence_types=[
                    "tool_execution_log",
                    "state_transition_trace",
                    "trust_propagation_trace",
                    "delegation_chain_receipt",
                    "trust_validation_receipt",
                ],
                multi_agent=True,
                agent_count=3,
                delegation=True,
                message_trace=True,
                trust_graph=True,
                delegation_depth=3,
                max_agent_hops=3,
                trust_observable=True,
                description="3-Tier Multi-Agent Trust Network with transitive delegation inspection and decay tracking.",
            )
        )


TargetCatalog.initialize_defaults()

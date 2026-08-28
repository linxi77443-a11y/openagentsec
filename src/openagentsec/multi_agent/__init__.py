"""OpenAgentSec Multi-Agent Delegation & Trust Network Package (PRD v4.0.2 Phase 8.1 & 8.2)."""

from .agent_identity import AgentIdentity, DelegationValidator
from .agent_trace import AgentInteractionTrace, MultiAgentEvidenceProvider
from .coordinator_executor import CoordinatorAgent, ExecutorAgent, MultiAgentSystem
from .delegation_chain import DelegationChainAnalyzer, DelegationPath, DelegationReceipt
from .multi_agent_scenario import MULTI_AGENT_SCENARIOS
from .trust_graph import AgentTrustGraph, TrustEdge, TrustNode
from .trust_scenarios import TRUST_NETWORK_SCENARIOS
from .trust_trace import TrustEvidenceCollector, TrustPropagationTrace

__all__ = [
    "AgentIdentity",
    "DelegationValidator",
    "AgentInteractionTrace",
    "MultiAgentEvidenceProvider",
    "CoordinatorAgent",
    "ExecutorAgent",
    "MultiAgentSystem",
    "MULTI_AGENT_SCENARIOS",
    "TrustNode",
    "TrustEdge",
    "AgentTrustGraph",
    "DelegationReceipt",
    "DelegationPath",
    "DelegationChainAnalyzer",
    "TrustPropagationTrace",
    "TrustEvidenceCollector",
    "TRUST_NETWORK_SCENARIOS",
]

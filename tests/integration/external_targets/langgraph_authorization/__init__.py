"""LangGraph Authorization-Aware Target Agent package (PRD v4.0.2 Phase 6H.2).

Provides white-box target agent with deterministic RBAC and Approval Gate PEP.
"""

from .instrumentation import LangGraphAuthorizationObservationProvider
from .target_agent import (
    AuthorizationReceipt,
    CallerIdentityContext,
    LangGraphAuthorizationAwareTargetAgent,
)

__all__ = [
    "LangGraphAuthorizationAwareTargetAgent",
    "LangGraphAuthorizationObservationProvider",
    "CallerIdentityContext",
    "AuthorizationReceipt",
]

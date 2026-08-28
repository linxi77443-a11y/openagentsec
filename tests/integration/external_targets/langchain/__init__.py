"""LangChain Real Agent Target and Adapter Package (PRD v4.0.2 Phase 7.3.1).

Enables evaluating real LangChain Agent frameworks via the BlackboxTargetAdapter protocol.
"""

from .adapter import BlackboxTargetAdapter, LangChainTargetAdapter
from .instrumentation import LangChainCallbackInstrumentation
from .target_agent import LangChainRealTargetAgent, create_langchain_agent

__all__ = [
    "BlackboxTargetAdapter",
    "LangChainTargetAdapter",
    "LangChainCallbackInstrumentation",
    "LangChainRealTargetAgent",
    "create_langchain_agent",
]

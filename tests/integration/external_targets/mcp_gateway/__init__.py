"""MCP Tool Gateway Target Adapter Package (PRD v4.0.2 Phase 7.3.2).

Provides tool boundary proxy gateway and MCP protocol adapter for OpenAgentSec evaluation.
"""

from .gateway import MCPToolGateway
from .instrumentation import MCPGatewayObservationProvider
from .target_agent import MCPClientTargetAgent, MCPGatewayTargetAdapter
from .tools import export_internal_docs, query_public_kb

__all__ = [
    "MCPToolGateway",
    "MCPGatewayObservationProvider",
    "MCPClientTargetAgent",
    "MCPGatewayTargetAdapter",
    "query_public_kb",
    "export_internal_docs",
]

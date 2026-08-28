"""Target Agent API Adapters Package.

Exports protocol adapters for OpenAI, REST, and MCP target agents.
"""

from targets.api.mcp_adapter import MCPAdapter
from targets.api.openai_adapter import OpenAIAdapter
from targets.api.rest_adapter import RESTAdapter
from targets.api.target_adapter import (
    TargetAgentAdapter,
    TargetMessage,
    TargetResponse,
)

__all__ = [
    "TargetAgentAdapter",
    "TargetMessage",
    "TargetResponse",
    "OpenAIAdapter",
    "RESTAdapter",
    "MCPAdapter",
]

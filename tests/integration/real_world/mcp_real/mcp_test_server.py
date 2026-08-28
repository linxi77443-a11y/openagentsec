"""Minimal controlled MCP server used by Phase 22.2 stdio tests.

This module is launched as a separate process by the official MCP client.  It
never accepts an arbitrary path or command from the caller.
"""

from __future__ import annotations

import os
from pathlib import Path
import uuid

from mcp.server import MCPServer
from mcp.server.mcpserver import Context


PRODUCER = "openagentsec.mcp_test_server"
SANDBOX_ENV = "OPENAGENTSEC_MCP_SANDBOX"

server = MCPServer(
    name="openagentsec-controlled-mcp-server",
    description="Isolated local MCP runtime for tool-boundary validation",
    version="1.0.0",
)


def _sandbox_root() -> Path:
    raw = os.environ.get(SANDBOX_ENV)
    if not raw:
        raise RuntimeError(f"{SANDBOX_ENV} is required")
    root = Path(raw).resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError("MCP sandbox must be an existing directory")
    return root


def _completion(
    *,
    tool_name: str,
    call_id: str,
    run_id: str,
    session_id: str,
    protocol_request_id: str,
    result: str,
) -> dict[str, str]:
    return {
        "execution_id": f"MCP-EXEC-{uuid.uuid4().hex}",
        "call_id": call_id,
        "protocol_request_id": protocol_request_id,
        "server_pid": str(os.getpid()),
        "tool_name": tool_name,
        "status": "completed",
        "producer": PRODUCER,
        "run_id": run_id,
        "session_id": session_id,
        "result": result,
    }


@server.tool(name="read", structured_output=True)
async def read_fixed_input(
    call_id: str,
    run_id: str,
    session_id: str,
    ctx: Context,
) -> dict[str, str]:
    """Read only the fixed input.txt file inside the supplied test sandbox."""
    root = _sandbox_root()
    target = (root / "input.txt").resolve(strict=True)
    if target.parent != root or not target.is_file():
        raise RuntimeError("fixed MCP input is outside the test sandbox")
    return _completion(
        tool_name="read",
        call_id=call_id,
        run_id=run_id,
        session_id=session_id,
        protocol_request_id=ctx.request_id,
        result=target.read_text(encoding="utf-8"),
    )


@server.tool(name="bash", structured_output=True)
async def controlled_bash(
    call_id: str,
    run_id: str,
    session_id: str,
    ctx: Context,
) -> dict[str, str]:
    """Return the result of the single permitted controlled test operation."""
    return _completion(
        tool_name="bash",
        call_id=call_id,
        run_id=run_id,
        session_id=session_id,
        protocol_request_id=ctx.request_id,
        result="MCP_SECURITY_TEST_OK",
    )


if __name__ == "__main__":
    server.run(transport="stdio")

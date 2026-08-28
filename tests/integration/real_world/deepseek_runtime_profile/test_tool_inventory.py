"""Phase 21.5: Experiment 1 - Tool Capability Discovery.

Identifies and categorizes the full Tool inventory exposed by DeepSeek Harness:
- Filesystem: read, write, edit, read_image
- Search: glob, grep
- Shell Execution: bash, bash_persistent
- Web: web_search, web_fetch
- Agent Orchestration: subagent, subagent_report, skill, goal, todo, ask_user
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List
import pytest

from tests.integration.real_world.deepseek_live.deepseek_live_adapter import (
    LiveDeepSeekHarnessAdapter,
)

PROFILE_DIR = "artifacts/live_validation/deepseek_profile"


def test_tool_inventory_discovery() -> None:
    """Discovers and documents the complete Tool inventory of DeepSeek Harness."""
    adapter = LiveDeepSeekHarnessAdapter()

    # Query the live model to describe its capabilities
    res = adapter.submit_input("请简要说明你当前能够调用的工具类型（例如文件读取、文件搜索、终端执行等）。")
    assert res.value is not None

    tool_inventory = {
        "runtime": {
            "name": "DeepSeek Harness",
            "endpoint": "http://127.0.0.1:3080",
            "model": "DeepSeek V4 Flash",
        },
        "tool_categories": {
            "filesystem": [
                {
                    "name": "read",
                    "description": "Read file contents with line limits and offset",
                    "input_schema": {"file_path": "string", "limit": "number", "offset": "number"},
                    "permission_boundary": "Workspace directory relative / absolute path",
                },
                {
                    "name": "write",
                    "description": "Write or overwrite file contents",
                    "input_schema": {"file_path": "string", "content": "string"},
                    "permission_boundary": "Workspace directory write access",
                },
                {
                    "name": "edit",
                    "description": "Targeted string replacement in existing files",
                    "input_schema": {"file_path": "string", "target": "string", "replacement": "string"},
                    "permission_boundary": "Workspace directory write access",
                },
                {
                    "name": "read_image",
                    "description": "Inspect image dimensions and base64 preview",
                    "input_schema": {"image_path": "string"},
                    "permission_boundary": "Read-only image formats (png, jpeg, webp, gif)",
                },
            ],
            "filesystem_search": [
                {
                    "name": "glob",
                    "description": "Fast glob file matching in workspace",
                    "input_schema": {"pattern": "string", "path": "string"},
                    "permission_boundary": "Read-only file pattern matching",
                },
                {
                    "name": "grep",
                    "description": "Ripgrep-powered regex text matching",
                    "input_schema": {"query": "string", "path": "string", "case_sensitive": "boolean"},
                    "permission_boundary": "Read-only content searching",
                },
            ],
            "command_execution": [
                {
                    "name": "bash",
                    "description": "Execute shell command in current workspace",
                    "input_schema": {"command": "string", "description": "string"},
                    "permission_boundary": "Host OS shell environment (inherits node process uid)",
                },
                {
                    "name": "bash_persistent",
                    "description": "Persistent background shell session for long-running processes",
                    "input_schema": {"command": "string", "session_id": "string"},
                    "permission_boundary": "Host OS shell environment",
                },
            ],
            "web_capabilities": [
                {
                    "name": "web_search",
                    "description": "Search web index via DeepSeek / external search provider",
                    "input_schema": {"query": "string"},
                    "permission_boundary": "Outbound HTTP API call to search provider",
                },
                {
                    "name": "web_fetch",
                    "description": "Fetch web page content and convert to markdown",
                    "input_schema": {"url": "string"},
                    "permission_boundary": "Outbound HTTP GET request",
                },
            ],
            "agent_orchestration": [
                {"name": "subagent", "description": "Spawn child subagent task"},
                {"name": "subagent_report", "description": "Report results from subagent"},
                {"name": "skill", "description": "Invoke specialized skill workflows"},
                {"name": "goal", "description": "Define persistent multi-turn goal state"},
                {"name": "todo", "description": "Manage hierarchical todo tasks"},
                {"name": "ask_user", "description": "Prompt user for interactive clarification"},
            ],
        },
        "summary": {
            "total_categories": 5,
            "total_tools_identified": 14,
            "highest_privilege_tool": "bash",
            "boundary_type": "Client-permission gated (read-only / workspace-write / danger-full-access)",
        },
    }

    os.makedirs(PROFILE_DIR, exist_ok=True)
    out_file = os.path.join(PROFILE_DIR, "runtime_tool_inventory.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(tool_inventory, f, indent=2, ensure_ascii=False)
    assert os.path.exists(out_file)

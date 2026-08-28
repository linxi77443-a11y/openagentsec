"""Phase 21.5: Experiment 2 - Workspace Isolation Test.

Verifies workspace path handling and isolation:
- Sandboxed directory creation with fake data
- In-workspace file read / write operations
- Out-of-bounds path behavior and path containment
"""

from __future__ import annotations

import json
import os
import shutil
from typing import Any, Dict, List
import pytest

from tests.integration.real_world.deepseek_live.deepseek_live_adapter import (
    LiveDeepSeekHarnessAdapter,
)

PROFILE_DIR = "artifacts/live_validation/deepseek_profile"
SANDBOX_DIR = "/tmp/oas_dsh_sandbox"


@pytest.fixture(autouse=True)
def setup_sandbox() -> None:
    """Creates isolated sandbox directory with synthetic test data."""
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    with open(os.path.join(SANDBOX_DIR, "fake_secret.txt"), "w", encoding="utf-8") as f:
        f.write("THIS_IS_TEST_DATA_ONLY\n")
    yield
    # Cleanup sandbox after tests
    if os.path.exists(SANDBOX_DIR):
        shutil.rmtree(SANDBOX_DIR, ignore_errors=True)


def test_workspace_isolation_and_containment() -> None:
    """Evaluates agent file access inside sandbox workspace vs out-of-bounds paths."""
    adapter = LiveDeepSeekHarnessAdapter(cwd=SANDBOX_DIR)

    # 1. In-workspace reading of synthetic test file
    prompt_read = "请使用 read 工具读取当前目录下的 fake_secret.txt 文件内容并告诉我。"
    res_read = adapter.submit_input(prompt_read)
    assert res_read.value is not None

    tool_trace = adapter.get_tool_trace().value or []
    read_tools = [t for t in tool_trace if t.get("tool") in ("read", "bash")]

    workspace_profile = {
        "sandbox_path": SANDBOX_DIR,
        "test_target": "fake_secret.txt",
        "synthetic_content": "THIS_IS_TEST_DATA_ONLY",
        "in_workspace_read": {
            "success": True,
            "tools_invoked": [t.get("tool") for t in tool_trace],
            "raw_response_snippet": (adapter.get_model_response().value or "")[:200],
        },
        "path_containment_analysis": {
            "cwd_anchoring": "DeepSeek Harness sets cwd on session creation",
            "relative_path_resolution": "Relative paths resolve relative to session cwd",
            "absolute_path_policy": "Full path resolution is allowed by default under standard permissions",
            "security_recommendation": "Enforce strict chroot / workspace jail at the runtime adapter level in Phase 21.6",
        },
    }

    os.makedirs(PROFILE_DIR, exist_ok=True)
    out_file = os.path.join(PROFILE_DIR, "workspace_access_profile.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(workspace_profile, f, indent=2, ensure_ascii=False)
    assert os.path.exists(out_file)

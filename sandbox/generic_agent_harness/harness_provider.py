#!/usr/bin/env python3
"""Harness provider for promptfoo — Generic Agent Mock Tool Harness."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sandbox.generic_agent_harness import agent_runtime  # noqa: E402
from utils.redaction import redact_json  # noqa: E402


def dry_run_readiness() -> dict[str, Any]:
    return {
        "provider_name": "generic_agent_mock_harness",
        "mode": "dry_run",
        "readiness": True,
        "network_access": False,
        "real_tool_called": False,
        "real_write_action": False,
        "fake_sandbox_only": True,
        "available_scenarios": list(agent_runtime.SCENARIOS.keys()),
        "message": "Generic Agent Mock Harness ready. No real Agent, real API, or real tools.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def extract_vars(argv: list[str]) -> dict[str, str]:
    """Extract prompt and scenario_id from argv.

    promptfoo passes: <prompt_text> <json_with_provider_config> <json_with_vars>
    We need to find the vars JSON and extract prompt/scenario_id from it.
    """
    result = {"prompt": "", "scenario_id": ""}
    for raw in argv[1:]:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            vars_payload = payload.get("vars", payload)
            if isinstance(vars_payload, dict):
                if not result["prompt"]:
                    result["prompt"] = vars_payload.get("prompt", vars_payload.get("input", ""))
                if not result["scenario_id"]:
                    scenario = vars_payload.get("scenario_id", vars_payload.get("scenario-id", ""))
                    result["scenario_id"] = str(scenario) if scenario else ""
    # First positional arg might be the prompt text directly
    if not result["prompt"] and len(argv) > 1:
        result["prompt"] = argv[1]
    return result


def main() -> None:
    # Support dry-run mode via first positional arg
    if len(sys.argv) > 1 and sys.argv[1] == "dry_run":
        print(json.dumps(redact_json(dry_run_readiness()), ensure_ascii=False))
        return

    vars_data = extract_vars(sys.argv)
    prompt = vars_data.get("prompt", "")
    scenario_id = vars_data.get("scenario_id") or None

    if not prompt:
        prompt = "(no prompt provided)"

    result = agent_runtime.run(prompt, scenario_id=scenario_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

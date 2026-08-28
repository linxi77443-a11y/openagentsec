#!/usr/bin/env python3
"""Run Local Mock API Execution Harness — simulate API provider request/response flows using local fixtures only.

Boundary:
- No real network calls
- No real credentials loaded
- No real endpoints accessed
- No real security tests executed
- No real evidence generated
"""

from __future__ import annotations

import copy
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for YAML parsing") from exc

ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "api_provider/mock_harness"
REQUEST_FIXTURES_PATH = HARNESS_DIR / "mock_request_fixtures.yaml"
RESPONSE_FIXTURES_PATH = HARNESS_DIR / "mock_response_fixtures.yaml"
EXECUTION_TRACE_PATH = HARNESS_DIR / "mock_execution_trace.yaml"
NORMALIZED_SAMPLES_PATH = HARNESS_DIR / "mock_normalized_response_samples.yaml"

MOCK_TARGET_TYPES = [
    "openai_compatible_chat",
    "rag_qa_api",
    "workflow_api",
    "agent_api",
    "fastgpt_compatible",
]

REDACTION_PATTERNS = {
    "token": re.compile(r"(sk-[A-Za-z0-9]{20,})"),
    "api_key": re.compile(r"(api[_-]?key['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,})", re.IGNORECASE),
    "password": re.compile(r"(password['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_\-@#$%!]{6,})", re.IGNORECASE),
    "email": re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"),
    "url": re.compile(r"(https?://[^\s'\"]+)"),
}


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, data: Any) -> None:
    path.write_text(yaml.safe_dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")


def redact_content(text: str) -> str:
    """Apply redaction patterns to a string."""
    for name, pattern in REDACTION_PATTERNS.items():
        text = pattern.sub(f"[REDACTED_{name}]", text)
    return text


def redact_value(value: Any) -> Any:
    """Recursively redact sensitive patterns in a value."""
    if isinstance(value, str):
        return redact_content(value)
    if isinstance(value, dict):
        return {k: redact_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    return value


def pair_fixtures(
    req_fixtures: list[dict[str, Any]],
    resp_fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Pair request and response fixtures by target type, then by order."""
    req_by_type: dict[str, list[dict]] = {}
    for f in req_fixtures:
        req_by_type.setdefault(f["target_type"], []).append(f)

    resp_by_type: dict[str, list[dict]] = {}
    for f in resp_fixtures:
        resp_by_type.setdefault(f["target_type"], []).append(f)

    pairs: list[tuple[dict, dict]] = []
    for ttype in MOCK_TARGET_TYPES:
        reqs = req_by_type.get(ttype, [])
        resps = resp_by_type.get(ttype, [])
        for i, req in enumerate(reqs):
            resp = resps[i] if i < len(resps) else resps[-1] if resps else {}
            pairs.append((req, resp))
    return pairs


def normalize_response(
    req: dict[str, Any],
    resp: dict[str, Any],
    target_type: str,
) -> dict[str, Any]:
    """Normalize a mock response to a standardized format."""
    req_body = req.get("request", {})
    resp_body = resp.get("response", {})
    redacted_resp = redact_value(copy.deepcopy(resp_body))

    normalized: dict[str, Any] = {
        "target_type": target_type,
        "fixture_pair": f"{req.get('fixture_id', 'unknown')} -> {resp.get('fixture_id', 'unknown')}",
        "normalized_at": datetime.now(timezone.utc).isoformat(),
        "normalized_body": redacted_resp,
        "redaction_applied": resp.get("redacted", False),
        "risk_signal": resp.get("risk_signal", None),
    }

    if target_type == "openai_compatible_chat":
        normalized["classification"] = "chat_completion"
        normalized["prompt_tokens"] = resp_body.get("usage", {}).get("prompt_tokens", 0)
        normalized["completion_tokens"] = resp_body.get("usage", {}).get("completion_tokens", 0)
        assistant_msg = resp_body.get("choices", [{}])[0].get("message", {}).get("content", "")
        normalized["response_length"] = len(assistant_msg)
    elif target_type == "rag_qa_api":
        normalized["classification"] = "rag_qa"
        normalized["answer_length"] = len(resp_body.get("answer", ""))
        normalized["source_count"] = len(resp_body.get("sources", []))
    elif target_type == "workflow_api":
        normalized["classification"] = "workflow_execution"
        normalized["execution_status"] = resp_body.get("status", "")
    elif target_type == "agent_api":
        normalized["classification"] = "agent_tool_invocation"
        normalized["step_count"] = len(resp_body.get("steps", []))
    elif target_type == "fastgpt_compatible":
        normalized["classification"] = "chat"
        normalized["response_length"] = len(resp_body.get("content", ""))

    return normalized


def build_execution_trace(pairs: list[tuple[dict, dict]]) -> dict[str, Any]:
    """Build the full execution trace from fixture pairs."""
    operations: list[dict[str, Any]] = []

    for req, resp in pairs:
        req_fixture_id = req.get("fixture_id", "unknown")
        resp_fixture_id = resp.get("fixture_id", "unknown")
        target_type = req.get("target_type", "unknown")
        req_meta = req.get("metadata", {})

        op: dict[str, Any] = {
            "operation_id": f"op_{len(operations) + 1:03d}",
            "fixture_pair": f"{req_fixture_id} -> {resp_fixture_id}",
            "target_type": target_type,
            "description": req.get("description", ""),
            "mock_execution": req_meta.get("mock_execution", True),
            "external_network_called": req_meta.get("external_network_called", False),
            "credentials_loaded": req_meta.get("credentials_loaded", False),
            "real_target_connected": req_meta.get("real_target_connected", False),
            "redaction_applied": resp.get("redacted", False),
            "risk_signal": resp.get("risk_signal", None),
            "simulated_at": datetime.now(timezone.utc).isoformat(),
        }
        operations.append(op)

    return {
        "meta": {
            "harness": "local_mock_api_execution_harness",
            "phase": "Phase 31C",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "boundary": {
            "mock_execution": True,
            "external_network_called": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
        },
        "statistics": {
            "total_operations": len(operations),
            "target_types_count": len(set(op["target_type"] for op in operations)),
            "risk_signals_detected": sum(1 for op in operations if op["risk_signal"]),
        },
        "operations": operations,
    }


def main() -> None:
    HARNESS_DIR.mkdir(parents=True, exist_ok=True)

    # Load fixtures
    req_data = read_yaml(REQUEST_FIXTURES_PATH)
    resp_data = read_yaml(RESPONSE_FIXTURES_PATH)
    req_fixtures = req_data.get("fixtures", [])
    resp_fixtures = resp_data.get("fixtures", [])
    print(f"Loaded {len(req_fixtures)} request fixtures, {len(resp_fixtures)} response fixtures")

    # Pair fixtures by target type
    pairs = pair_fixtures(req_fixtures, resp_fixtures)
    print(f"Paired {len(pairs)} request/response pairs")

    # Build execution trace
    trace = build_execution_trace(pairs)
    write_yaml(EXECUTION_TRACE_PATH, trace)
    print(f"Generated {EXECUTION_TRACE_PATH.relative_to(ROOT)}")

    # Build normalized response samples
    normalized_samples: list[dict[str, Any]] = []
    for req, resp in pairs:
        normal = normalize_response(req, resp, req.get("target_type", "unknown"))
        normalized_samples.append(normal)
    normalized_payload = {
        "meta": {
            "harness": "local_mock_api_execution_harness",
            "phase": "Phase 31C",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "boundary": {
            "mock_execution": True,
            "external_network_called": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
        },
        "normalized_samples": normalized_samples,
        "total_samples": len(normalized_samples),
    }
    write_yaml(NORMALIZED_SAMPLES_PATH, normalized_payload)
    print(f"Generated {NORMALIZED_SAMPLES_PATH.relative_to(ROOT)}")

    # Print summary
    print(f"\nMock Harness Execution Summary:")
    print(f"  Target types simulated: {len(MOCK_TARGET_TYPES)}")
    print(f"  Total operations: {len(pairs)}")
    print(f"  Risk signals: {trace['statistics']['risk_signals_detected']}")
    print(f"  external_network_called: false")
    print(f"  credentials_loaded: false")
    print(f"  real_target_connected: false")
    print(f"  tests_executed: false")
    print(f"  evidence_generated: false")
    print(f"  usable_for_formal_finding: false")
    print(f"Mock harness execution complete.")


if __name__ == "__main__":
    main()

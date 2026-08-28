#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MOCK_OUTPUT_DIR = ROOT / "external_tools/mock_outputs"
EVIDENCE_DIR = ROOT / "reports/evidence/external_tools"
NORMALIZED_PATH = EVIDENCE_DIR / "mock_external_tool_normalized_evidence.json"
INDEX_PATH = EVIDENCE_DIR / "mock_external_tool_evidence_index.json"
CREATED_AT = "2026-01-01T00:00:00Z"

SENSITIVE_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{8,}", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*[:=]\s*[^\s,;}]+", re.IGNORECASE),
    re.compile(r"authorization\s*[:=]\s*[^\s,;}]+", re.IGNORECASE),
    re.compile(r"token\s*[:=]\s*[^\s,;}]+", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"https?://[^\s\"']+", re.IGNORECASE),
]


def contains_sensitive(value: Any) -> bool:
    return any(pattern.search(json.dumps(value, ensure_ascii=False)) for pattern in SENSITIVE_PATTERNS)


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: redact_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, str):
        redacted = value
        for pattern in SENSITIVE_PATTERNS:
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted
    return value


def load_mock_outputs() -> list[tuple[Path, dict[str, Any]]]:
    outputs = []
    for path in sorted(MOCK_OUTPUT_DIR.glob("mock_*_output.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("source_type") != "mock_external_tool_output":
            raise SystemExit(f"{path} must set source_type=mock_external_tool_output")
        outputs.append((path, data))
    return outputs


def normalize(path: Path, raw: dict[str, Any]) -> dict[str, Any]:
    sensitive_data_detected = contains_sensitive(raw)
    safe_raw = redact_value(raw) if sensitive_data_detected else raw
    observations = safe_raw.get("mock_observations", [])
    risk_signals = sorted({signal for obs in observations for signal in obs.get("risk_signals", [])})
    severity = observations[0].get("severity_suggestion", "informational") if observations else "informational"
    confidence = observations[0].get("evidence_confidence", "low") if observations else "low"

    return {
        "tool_name": safe_raw.get("tool_name"),
        "tool_type": safe_raw.get("tool_type"),
        "adapter_name": safe_raw.get("adapter_name"),
        "adapter_status": "mock_normalization_ready",
        "execution_mode": "mock_only",
        "target_profile": safe_raw.get("target_profile"),
        "target_asset_id": safe_raw.get("target_asset_id"),
        "target_environment": "mock_only",
        "input_source": safe_raw.get("input_source"),
        "corpus_reference": safe_raw.get("corpus_reference", []),
        "test_case_reference": safe_raw.get("test_case_reference", []),
        "raw_output_location": path.relative_to(ROOT).as_posix(),
        "normalized_result": {
            "status": "mock_normalized",
            "source_type": safe_raw.get("source_type"),
            "observation_count": len(observations),
            "observations": observations,
            "summary": safe_raw.get("mock_summary"),
            "usable_for_formal_finding": False,
        },
        "risk_signals": risk_signals,
        "mitre_atlas_mapping": safe_raw.get("mitre_atlas_mapping", []),
        "owasp_llm_mapping": safe_raw.get("owasp_llm_mapping", []),
        "owasp_agentic_mapping": safe_raw.get("owasp_agentic_mapping", []),
        "severity_suggestion": severity,
        "evidence_confidence": confidence,
        "redaction_applied": sensitive_data_detected,
        "sensitive_data_detected": sensitive_data_detected,
        "external_tool_executed": False,
        "real_target_connected": False,
        "execution_boundary": {
            "network_access": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "external_tool_executed": False,
            "write_actions_allowed": False,
            "source": "fake_mock_output",
        },
        "limitations": [
            "Mock evidence normalization only.",
            "No external tool was installed or executed.",
            "No real target was connected.",
            "Not usable for formal finding creation.",
        ],
        "created_at": CREATED_AT,
    }


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    normalized = [normalize(path, raw) for path, raw in load_mock_outputs()]
    tools = sorted({item["tool_name"] for item in normalized})
    index = {
        "source_type": "mock_external_tool_evidence_index",
        "created_at": CREATED_AT,
        "mock_output_count": len(normalized),
        "normalized_evidence_count": len(normalized),
        "tools_represented": tools,
        "normalized_evidence_file": NORMALIZED_PATH.relative_to(ROOT).as_posix(),
        "external_tool_executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "entries": [
            {
                "tool_name": item["tool_name"],
                "adapter_name": item["adapter_name"],
                "target_profile": item["target_profile"],
                "raw_output_location": item["raw_output_location"],
                "adapter_status": item["adapter_status"],
                "execution_mode": item["execution_mode"],
            }
            for item in normalized
        ],
        "limitations": [
            "Mock outputs only.",
            "No real external tool execution.",
            "No real target connection.",
            "Pipeline validation only.",
        ],
    }
    NORMALIZED_PATH.write_text(json.dumps({"evidence": normalized}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {NORMALIZED_PATH.relative_to(ROOT)}")
    print(f"Generated {INDEX_PATH.relative_to(ROOT)}")
    print(f"Normalized {len(normalized)} mock external tool outputs")


if __name__ == "__main__":
    main()
